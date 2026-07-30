from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, Q
from django.utils import timezone

from .models import Category, Income, Expense, Budget, SavingsGoal
from .forms import CategoryForm, IncomeForm, ExpenseForm, BudgetForm, SavingsGoalForm

# ----------------- Dashboard View -----------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # Monthly calculations
        monthly_incomes = Income.objects.filter(
            user=user, date__month=current_month, date__year=current_year
        )
        monthly_expenses = Expense.objects.filter(
            user=user, date__month=current_month, date__year=current_year
        )

        total_income = monthly_incomes.aggregate(total=Sum('amount'))['total'] or 0
        total_expense = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0
        balance = total_income - total_expense

        # Total savings reached
        active_goals = SavingsGoal.objects.filter(user=user, is_completed=False)
        total_savings = active_goals.aggregate(total=Sum('current_amount'))['total'] or 0

        # Recent transactions (merge Income and Expense)
        recent_incomes = list(Income.objects.filter(user=user)[:5])
        recent_expenses = list(Expense.objects.filter(user=user)[:5])
        recent_transactions = sorted(
            recent_incomes + recent_expenses,
            key=lambda x: x.date,
            reverse=True
        )[:5]

        # Budgets warning check
        active_budgets = Budget.objects.filter(
            user=user, start_date__lte=now.date(), end_date__gte=now.date()
        )
        exceeded_budgets_count = 0
        for budget in active_budgets:
            if budget.current_spending > budget.amount:
                exceeded_budgets_count += 1

        context.update({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'total_savings': total_savings,
            'recent_transactions': recent_transactions,
            'active_goals': active_goals[:3],
            'active_budgets': active_budgets[:3],
            'exceeded_budgets_count': exceeded_budgets_count,
            'income_form': IncomeForm(user=user),
            'expense_form': ExpenseForm(user=user),
        })
        return context

# ----------------- Category Views -----------------

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'tracker/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Show global categories and user's custom categories
        return Category.objects.filter(Q(user=self.request.user) | Q(user__isnull=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CategoryForm()
        return context

class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'tracker/category_list.html'
    success_url = reverse_lazy('category_list')
    success_message = "Category created successfully."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'tracker/category_form.html'
    success_url = reverse_lazy('category_list')
    success_message = "Category updated successfully."

    def get_queryset(self):
        # Users can only edit their own categories
        return Category.objects.filter(user=self.request.user)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'tracker/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        category = self.get_object()
        # Prevent deletion if referenced by incomes/expenses
        if Income.objects.filter(category=category).exists() or Expense.objects.filter(category=category).exists():
            messages.error(request, "This category is in use and cannot be deleted.")
            return redirect('category_list')
        messages.success(request, "Category deleted successfully.")
        return super().post(request, *args, **kwargs)

# ----------------- Income Views -----------------

class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'tracker/income_list.html'
    context_object_name = 'incomes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Income.objects.filter(user=self.request.user)
        # Search & Filter
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if q:
            queryset = queryset.filter(description__icontains=q)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['income_categories'] = Category.objects.filter(
            Q(type='INCOME') & (Q(user=self.request.user) | Q(user__isnull=True))
        )
        context['filter_category'] = self.request.GET.get('category', '')
        context['filter_q'] = self.request.GET.get('q', '')
        context['filter_start_date'] = self.request.GET.get('start_date', '')
        context['filter_end_date'] = self.request.GET.get('end_date', '')
        return context

class IncomeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'tracker/income_form.html'
    success_url = reverse_lazy('income_list')
    success_message = "Income transaction added."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class IncomeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'tracker/income_form.html'
    success_url = reverse_lazy('income_list')
    success_message = "Income transaction updated."

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class IncomeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Income
    template_name = 'tracker/income_confirm_delete.html'
    success_url = reverse_lazy('income_list')
    success_message = "Income transaction deleted."

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

# ----------------- Expense Views -----------------

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'tracker/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 10

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user)
        # Search & Filter
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if q:
            queryset = queryset.filter(description__icontains=q)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_categories'] = Category.objects.filter(
            Q(type='EXPENSE') & (Q(user=self.request.user) | Q(user__isnull=True))
        )
        context['filter_category'] = self.request.GET.get('category', '')
        context['filter_q'] = self.request.GET.get('q', '')
        context['filter_start_date'] = self.request.GET.get('start_date', '')
        context['filter_end_date'] = self.request.GET.get('end_date', '')
        return context

class ExpenseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'tracker/expense_form.html'
    success_url = reverse_lazy('expense_list')
    success_message = "Expense transaction added."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Check budget alert when adding expense
        response = super().form_valid(form)
        self.check_budget_limits(self.object)
        return response

    def check_budget_limits(self, expense):
        # Look for active budget for the category of the new expense
        active_budgets = Budget.objects.filter(
            user=self.request.user,
            category=expense.category,
            start_date__lte=expense.date,
            end_date__gte=expense.date
        )
        for budget in active_budgets:
            spending = budget.current_spending
            if spending > budget.amount:
                messages.warning(
                    self.request,
                    f"CRITICAL ALERT: You have EXCEEDED your budget of {budget.amount} for {budget.category.name}! Current spending is {spending}."
                )
            elif spending >= budget.amount * 0.9:
                messages.warning(
                    self.request,
                    f"WARNING: You have spent 90% or more of your budget of {budget.amount} for {budget.category.name}! Current spending is {spending}."
                )
            elif spending >= budget.amount * 0.75:
                messages.info(
                    self.request,
                    f"NOTICE: You have spent 75% or more of your budget of {budget.amount} for {budget.category.name}. Current spending is {spending}."
                )

class ExpenseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'tracker/expense_form.html'
    success_url = reverse_lazy('expense_list')
    success_message = "Expense transaction updated."

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.check_budget_limits(self.object)
        return response

    def check_budget_limits(self, expense):
        # Same check on update
        active_budgets = Budget.objects.filter(
            user=self.request.user,
            category=expense.category,
            start_date__lte=expense.date,
            end_date__gte=expense.date
        )
        for budget in active_budgets:
            spending = budget.current_spending
            if spending > budget.amount:
                messages.warning(self.request, f"CRITICAL ALERT: You have EXCEEDED your budget for {budget.category.name}! Spent: {spending}/{budget.amount}.")

class ExpenseDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Expense
    template_name = 'tracker/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')
    success_message = "Expense transaction deleted."

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

# ----------------- Budget Views -----------------

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'tracker/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BudgetForm(user=self.request.user)
        return context

class BudgetCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'tracker/budget_form.html'
    success_url = reverse_lazy('budget_list')
    success_message = "Budget created successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BudgetUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'tracker/budget_form.html'
    success_url = reverse_lazy('budget_list')
    success_message = "Budget updated successfully."

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class BudgetDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Budget
    template_name = 'tracker/budget_confirm_delete.html'
    success_url = reverse_lazy('budget_list')
    success_message = "Budget deleted successfully."

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

# ----------------- Savings Goal Views -----------------

class SavingsGoalListView(LoginRequiredMixin, ListView):
    model = SavingsGoal
    template_name = 'tracker/savings_list.html'
    context_object_name = 'savings_goals'

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SavingsGoalForm()
        return context

class SavingsGoalCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'tracker/savings_form.html'
    success_url = reverse_lazy('savings_list')
    success_message = "Savings Goal created."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class SavingsGoalUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'tracker/savings_form.html'
    success_url = reverse_lazy('savings_list')
    success_message = "Savings Goal updated."

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

class SavingsGoalDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = SavingsGoal
    template_name = 'tracker/savings_confirm_delete.html'
    success_url = reverse_lazy('savings_list')
    success_message = "Savings Goal deleted."

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

class AddSavingsContributionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
            goal.current_amount += Decimal(amount)
            goal.save()
            messages.success(request, f"Successfully contributed {amount} to '{goal.name}'!")
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, "Invalid amount entered. Please enter a positive number.")
        return redirect('savings_list')
