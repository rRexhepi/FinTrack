from django.db import models
from django.contrib.auth.models import User
import yfinance as yf

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
        return f"{self.category} - ${self.amount} on {self.date}"

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

    @property
    def purchase_price_per_share(self):
        try:
            data = yf.Ticker(self.ticker)
            historical_data = data.history(start=self.date_invested, end=self.date_invested)
            if not historical_data.empty:
                return historical_data['Close'][0]
        except Exception as e:
            print(f"Error fetching purchase price for {self.ticker}: {e}")
        return 0

    @property
    def current_value(self):
        try:
            data = yf.Ticker(self.ticker)
            current_price = data.history(period='1d')['Close'][0]
            shares = self.amount_invested / self.purchase_price_per_share if self.purchase_price_per_share else 0
            return current_price * shares
        except Exception as e:
            print(f"Error fetching current value for {self.ticker}: {e}")
        return 0

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
        return f"{self.category} - ${self.amount} per {self.period}"

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
