import yfinance as yf
from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=50)  # e.g., 'Monthly', 'Weekly')

    def __str__(self):
        return f"{self.user.username} - {self.category} Budget"

class Expense(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)  # New field for stock ticker
    amount_invested = models.DecimalField(max_digits=10, decimal_places=2)
    date_invested = models.DateField()

    @property
    def current_value(self):
        data = yf.Ticker(self.ticker)
        current_price = data.history(period='1d')['Close'][0]
        shares = self.amount_invested / self.purchase_price_per_share
        return current_price * shares

    @property
    def purchase_price_per_share(self):
        data = yf.Ticker(self.ticker)
        historical_data = data.history(start=self.date_invested, end=self.date_invested)
        if not historical_data.empty:
            return historical_data['Close'][0]
        else:
            return 0  # Handle the case where no data is available
