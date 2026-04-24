from django.contrib.auth.models import User
from django.db import models


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField(db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f"{self.category} - ${self.amount:.2f} on {self.date}"


class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    amount_invested = models.DecimalField(max_digits=10, decimal_places=2)
    date_invested = models.DateField()

    class Meta:
        ordering = ['-date_invested']
        verbose_name = 'Investment'
        verbose_name_plural = 'Investments'

    def __str__(self):
        return f"{self.name} ({self.ticker})"


class Budget(models.Model):
    PERIOD_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)

    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'

    def __str__(self):
        return f"{self.category} - ${self.amount:.2f} per {self.period}"


class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggestions')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Suggestion'
        verbose_name_plural = 'Suggestions'

    def __str__(self):
        return f"Suggestion for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
