import csv
from openpyxl import Workbook
from django.http import HttpResponse
from tracker.models import Income, Expense
from django.utils import timezone

def generate_csv_report(user, start_date=None, end_date=None, trans_type='ALL'):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Date', 'Category', 'Amount', 'Description'])

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
            transactions.append(['Income', i.date, i.category.name, i.amount, i.description])
    if trans_type in ['ALL', 'EXPENSE']:
        for e in expenses:
            transactions.append(['Expense', e.date, e.category.name, e.amount, e.description])

    # Sort transactions by date (descending)
    transactions.sort(key=lambda x: x[1], reverse=True)

    for row in transactions:
        writer.writerow(row)

    return response

def generate_excel_report(user, start_date=None, end_date=None, trans_type='ALL'):
    wb = Workbook()
    ws = wb.active
    ws.title = "Financial Summary"

    # Style header row
    headers = ['Type', 'Date', 'Category', 'Amount', 'Description']
    ws.append(headers)

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
            transactions.append(['Income', i.date.strftime('%Y-%m-%d'), i.category.name, float(i.amount), i.description])
    if trans_type in ['ALL', 'EXPENSE']:
        for e in expenses:
            transactions.append(['Expense', e.date.strftime('%Y-%m-%d'), e.category.name, float(e.amount), e.description])

    # Sort transactions by date (descending)
    transactions.sort(key=lambda x: x[1], reverse=True)

    for row in transactions:
        ws.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    wb.save(response)
    
    return response
