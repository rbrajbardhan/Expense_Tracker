from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Category(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=50, default='bi-tag', help_text="Bootstrap Icon class name, e.g. bi-cart")
    color = models.CharField(max_length=7, default='#6f42c1', help_text="Hex color, e.g. #6f42c1")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ('name', 'type', 'user')

    def __str__(self):
        owner = f" ({self.user.username})" if self.user else " (Global)"
        return f"{self.name} - {self.type}{owner}"

class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, limit_choices_to={'type': 'INCOME'})
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"+{self.amount} on {self.date} ({self.category.name})"

class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, limit_choices_to={'type': 'EXPENSE'})
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"-{self.amount} on {self.date} ({self.category.name})"

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, limit_choices_to={'type': 'EXPENSE'})
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()

    class Meta:
        unique_together = ('user', 'category', 'start_date', 'end_date')

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Budget for {self.category.name}: {self.amount} ({self.start_date} to {self.end_date})"

    @property
    def current_spending(self):
        # Calculate current spending for this category in the budget date range
        spending = Expense.objects.filter(
            user=self.user,
            category=self.category,
            date__range=[self.start_date, self.end_date]
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return spending

    @property
    def percentage_spent(self):
        if self.amount <= 0:
            return 0
        return min(round((float(self.current_spending) / float(self.amount)) * 100, 2), 100)

    @property
    def amount_exceeded(self):
        if self.current_spending > self.amount:
            return self.current_spending - self.amount
        return 0


class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['target_date', 'name']

    def clean(self):
        if self.target_date and self.target_date < timezone.now().date():
            raise ValidationError("Target date cannot be in the past.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.current_amount >= self.target_amount:
            self.is_completed = True
        else:
            self.is_completed = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Goal: {self.target_amount} (Current: {self.current_amount})"

    @property
    def percentage_reached(self):
        if self.target_amount <= 0:
            return 0
        return min(round((float(self.current_amount) / float(self.target_amount)) * 100, 2), 100)
