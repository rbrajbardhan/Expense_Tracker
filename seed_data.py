import os
import django

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from tracker.models import Category

def seed_categories():
    categories = [
        # Income Categories
        {'name': 'Salary', 'type': 'INCOME', 'icon': 'bi-cash-stack', 'color': '#10b981'},
        {'name': 'Freelance', 'type': 'INCOME', 'icon': 'bi-laptop', 'color': '#06b6d4'},
        {'name': 'Investments', 'type': 'INCOME', 'icon': 'bi-graph-up-arrow', 'color': '#3b82f6'},
        {'name': 'Other Income', 'type': 'INCOME', 'icon': 'bi-wallet2', 'color': '#6366f1'},
        
        # Expense Categories
        {'name': 'Groceries', 'type': 'EXPENSE', 'icon': 'bi-cart', 'color': '#f59e0b'},
        {'name': 'Rent / Housing', 'type': 'EXPENSE', 'icon': 'bi-house', 'color': '#ef4444'},
        {'name': 'Utilities', 'type': 'EXPENSE', 'icon': 'bi-lightning', 'color': '#eab308'},
        {'name': 'Entertainment', 'type': 'EXPENSE', 'icon': 'bi-film', 'color': '#ec4899'},
        {'name': 'Dining Out', 'type': 'EXPENSE', 'icon': 'bi-cup-hot', 'color': '#f97316'},
        {'name': 'Transport', 'type': 'EXPENSE', 'icon': 'bi-car-front', 'color': '#a855f7'},
        {'name': 'Health & Medical', 'type': 'EXPENSE', 'icon': 'bi-heart-pulse', 'color': '#d946ef'},
        {'name': 'Shopping', 'type': 'EXPENSE', 'icon': 'bi-bag', 'color': '#db2777'},
        {'name': 'Travel', 'type': 'EXPENSE', 'icon': 'bi-airplane', 'color': '#14b8a6'},
    ]

    for cat in categories:
        obj, created = Category.objects.get_or_create(
            name=cat['name'],
            type=cat['type'],
            user=None, # Global categories have user=None
            defaults={
                'icon': cat['icon'],
                'color': cat['color']
            }
        )
        if created:
            print(f"Created category: {cat['name']} ({cat['type']})")
        else:
            print(f"Category already exists: {cat['name']} ({cat['type']})")

if __name__ == '__main__':
    seed_categories()
