from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta

from tracker.models import Income, Expense, Budget, Category, SavingsGoal
from .ai_insights import get_ai_insights
from .reports import generate_csv_report, generate_excel_report

# ----------------- Analytics Layout -----------------

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

# ----------------- API endpoint for Charts -----------------

class ChartDataAPIView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now().date()
        
        # 1. Income vs Expense Trend (Past 6 Months)
        trend_labels = []
        income_data = []
        expense_data = []
        
        for i in range(5, -1, -1):
            month_date = today - relativedelta(months=i)
            month_name = month_date.strftime('%b %Y')
            trend_labels.append(month_name)
            
            incomes_sum = Income.objects.filter(
                user=user, date__month=month_date.month, date__year=month_date.year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            expenses_sum = Expense.objects.filter(
                user=user, date__month=month_date.month, date__year=month_date.year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            income_data.append(float(incomes_sum))
            expense_data.append(float(expenses_sum))

        # 2. Category Distribution (Current Month)
        category_labels = []
        category_sums = []
        category_colors = []
        
        expenses_curr_month = Expense.objects.filter(
            user=user, date__month=today.month, date__year=today.year
        )
        cat_data = expenses_curr_month.values('category__name', 'category__color').annotate(total=Sum('amount'))
        
        for item in cat_data:
            category_labels.append(item['category__name'])
            category_sums.append(float(item['total']))
            category_colors.append(item['category__color'] or '#6f42c1')

        # 3. Budget vs Actual comparison
        active_budgets = Budget.objects.filter(
            user=user, start_date__lte=today, end_date__gte=today
        )
        budget_categories = []
        budget_limits = []
        budget_actuals = []
        
        for b in active_budgets:
            budget_categories.append(b.category.name)
            budget_limits.append(float(b.amount))
            budget_actuals.append(float(b.current_spending))

        data = {
            'trends': {
                'labels': trend_labels,
                'income': income_data,
                'expense': expense_data
            },
            'categories': {
                'labels': category_labels,
                'data': category_sums,
                'colors': category_colors
            },
            'budgets': {
                'labels': budget_categories,
                'limits': budget_limits,
                'actuals': budget_actuals
            }
        }
        return JsonResponse(data)

# ----------------- AI Insights Page -----------------

class AIInsightsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/ai_insights.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        insights = get_ai_insights(user)
        context['insights'] = insights
        return context

# ----------------- Reports & Filter Page -----------------

class ReportPageView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/report_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Filters from request
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        trans_type = self.request.GET.get('type', 'ALL')

        incomes = Income.objects.filter(user=user)
        expenses = Expense.objects.filter(user=user)

        if start_date:
            incomes = incomes.filter(date__gte=start_date)
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            incomes = incomes.filter(date__lte=end_date)
            expenses = expenses.filter(date__lte=end_date)

        transactions = []
        if trans_type in ['ALL', 'INCOME']:
            for i in incomes:
                transactions.append({
                    'type': 'Income',
                    'date': i.date,
                    'category': i.category.name,
                    'category_color': i.category.color,
                    'category_icon': i.category.icon,
                    'amount': i.amount,
                    'description': i.description
                })
        if trans_type in ['ALL', 'EXPENSE']:
            for e in expenses:
                transactions.append({
                    'type': 'Expense',
                    'date': e.date,
                    'category': e.category.name,
                    'category_color': e.category.color,
                    'category_icon': e.category.icon,
                    'amount': e.amount,
                    'description': e.description
                })

        transactions.sort(key=lambda x: x['date'], reverse=True)

        context.update({
            'transactions': transactions,
            'filter_start_date': start_date or '',
            'filter_end_date': end_date or '',
            'filter_type': trans_type,
        })
        return context

# ----------------- Export API View -----------------

class ExportReportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        trans_type = request.GET.get('type', 'ALL')
        export_format = request.GET.get('format', 'csv')

        # Convert date strings to Date objects if they exist
        s_date = None
        e_date = None
        if start_date:
            s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        if export_format == 'excel':
            return generate_excel_report(user, s_date, e_date, trans_type)
        else:
            return generate_csv_report(user, s_date, e_date, trans_type)
