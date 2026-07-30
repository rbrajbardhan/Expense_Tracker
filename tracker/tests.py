from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from tracker.models import Category, Income, Expense, Budget, SavingsGoal

class TrackerTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='trackeruser',
            password='trackerpassword123',
            email='tracker@example.com'
        )
        self.client.login(username='trackeruser', password='trackerpassword123')
        
        # Create global categories
        self.inc_cat = Category.objects.create(name='Salary', type='INCOME')
        self.exp_cat = Category.objects.create(name='Groceries', type='EXPENSE')

    def test_category_creation(self):
        self.assertEqual(Category.objects.count(), 2)
        # Custom category
        custom_cat = Category.objects.create(
            name='Freelancing',
            type='INCOME',
            user=self.user
        )
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(custom_cat.user, self.user)

    def test_income_logging(self):
        income = Income.objects.create(
            user=self.user,
            amount=5000.00,
            category=self.inc_cat,
            date=timezone.now().date(),
            description='Monthly salary payout'
        )
        self.assertEqual(Income.objects.count(), 1)
        self.assertEqual(float(income.amount), 5000.00)

    def test_expense_logging_and_budget_calculation(self):
        # Create Budget
        start = timezone.now().date()
        end = start + timezone.timedelta(days=30)
        budget = Budget.objects.create(
            user=self.user,
            category=self.exp_cat,
            amount=500.00,
            start_date=start,
            end_date=end
        )
        
        # Log Expense
        expense = Expense.objects.create(
            user=self.user,
            amount=120.00,
            category=self.exp_cat,
            date=timezone.now().date(),
            description='Supermarket shopping'
        )

        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(float(budget.current_spending), 120.00)
        self.assertEqual(budget.percentage_spent, 24.00)
        self.assertFalse(budget.amount_exceeded > 0)

    def test_savings_goal(self):
        goal = SavingsGoal.objects.create(
            user=self.user,
            name='Emergency Fund',
            target_amount=1000.00,
            current_amount=200.00,
            target_date=timezone.now().date() + timezone.timedelta(days=180)
        )
        self.assertEqual(goal.percentage_reached, 20.00)
        self.assertFalse(goal.is_completed)

        # Update contribution
        goal.current_amount = 1000.00
        goal.save()
        self.assertTrue(goal.is_completed)
        self.assertEqual(goal.percentage_reached, 100.00)
