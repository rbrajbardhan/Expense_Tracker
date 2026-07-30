from django.urls import path
from .views import (
    DashboardView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    IncomeListView, IncomeCreateView, IncomeUpdateView, IncomeDeleteView,
    ExpenseListView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView,
    BudgetListView, BudgetCreateView, BudgetUpdateView, BudgetDeleteView,
    SavingsGoalListView, SavingsGoalCreateView, SavingsGoalUpdateView, SavingsGoalDeleteView,
    AddSavingsContributionView
)

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # Income
    path('income/', IncomeListView.as_view(), name='income_list'),
    path('income/add/', IncomeCreateView.as_view(), name='income_add'),
    path('income/<int:pk>/edit/', IncomeUpdateView.as_view(), name='income_edit'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='income_delete'),

    # Expenses
    path('expenses/', ExpenseListView.as_view(), name='expense_list'),
    path('expenses/add/', ExpenseCreateView.as_view(), name='expense_add'),
    path('expenses/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense_edit'),
    path('expenses/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense_delete'),

    # Budgets
    path('budgets/', BudgetListView.as_view(), name='budget_list'),
    path('budgets/add/', BudgetCreateView.as_view(), name='budget_add'),
    path('budgets/<int:pk>/edit/', BudgetUpdateView.as_view(), name='budget_edit'),
    path('budgets/<int:pk>/delete/', BudgetDeleteView.as_view(), name='budget_delete'),

    # Savings Goals
    path('savings/', SavingsGoalListView.as_view(), name='savings_list'),
    path('savings/add/', SavingsGoalCreateView.as_view(), name='savings_add'),
    path('savings/<int:pk>/edit/', SavingsGoalUpdateView.as_view(), name='savings_edit'),
    path('savings/<int:pk>/delete/', SavingsGoalDeleteView.as_view(), name='savings_delete'),
    path('savings/<int:pk>/contribute/', AddSavingsContributionView.as_view(), name='savings_contribute'),
]
