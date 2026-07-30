from django.contrib import admin
from .models import Category, Income, Expense, Budget, SavingsGoal

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'icon', 'color', 'user']
    list_filter = ['type', 'user']
    search_fields = ['name']

class IncomeAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description', 'user__username']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description', 'user__username']

class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'start_date', 'end_date']
    list_filter = ['category', 'start_date', 'end_date']
    search_fields = ['user__username']

class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'target_amount', 'current_amount', 'target_date', 'is_completed']
    list_filter = ['is_completed', 'target_date']
    search_fields = ['name', 'user__username']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Income, IncomeAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(SavingsGoal, SavingsGoalAdmin)
