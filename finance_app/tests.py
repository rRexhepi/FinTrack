# finance_app/tests.py

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from . import market_data
from .models import Budget, Expense, Investment


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.expense = Expense.objects.create(
            user=self.user,
            date='2023-01-01',
            category='Food',
            amount=50.00,
            description='Groceries'
        )

    def test_expense_creation(self):
        self.assertEqual(self.expense.amount, 50.00)
        self.assertEqual(str(self.expense), "Food - $50.00 on 2023-01-01")

class InvestmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='investor', password='investpass')
        self.investment = Investment.objects.create(
            user=self.user,
            name='Apple Inc.',
            ticker='AAPL',
            amount_invested=1000.00,
            date_invested='2022-01-01'
        )

    def test_investment_creation(self):
        self.assertEqual(self.investment.name, 'Apple Inc.')
        self.assertEqual(str(self.investment), "Apple Inc. (AAPL)")

class BudgetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='budgetuser', password='budgetpass')
        self.budget = Budget.objects.create(
            user=self.user,
            category='Entertainment',
            amount=200.00,
            period='Monthly'
        )

    def test_budget_creation(self):
        self.assertEqual(self.budget.amount, 200.00)
        self.assertEqual(str(self.budget), "Entertainment - $200.00 per Monthly")

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apitestuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_get_expenses(self):
        response = self.client.get(reverse('expense-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_expense(self):
        data = {
            'date': '2023-01-01',
            'category': 'Transport',
            'amount': 20.00,
            'description': 'Bus ticket'
        }
        response = self.client.post(reverse('expense-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.get().category, 'Transport')

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('expense-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MarketDataTest(TestCase):
    """Unit tests for the yfinance wrapper + cache."""

    def setUp(self):
        cache.clear()

    def _fake_history(self, close_values, index_dates):
        return pd.DataFrame(
            {'Close': close_values},
            index=pd.to_datetime(index_dates),
        )

    def test_current_price_caches_first_result(self):
        fake = self._fake_history([123.45], ['2024-01-02'])
        ticker_mock = MagicMock()
        ticker_mock.history.return_value = fake

        with patch('finance_app.market_data.yf.Ticker', return_value=ticker_mock) as yf_ticker:
            first = market_data.get_current_price('AAPL')
            second = market_data.get_current_price('AAPL')

        self.assertEqual(first, Decimal('123.45'))
        self.assertEqual(second, Decimal('123.45'))
        # Key assertion: repeated calls don't re-hit yfinance. Before the
        # refactor, every dashboard serialization did N synchronous calls.
        yf_ticker.assert_called_once_with('AAPL')
        self.assertEqual(ticker_mock.history.call_count, 1)

    def test_current_price_returns_none_on_empty_frame(self):
        ticker_mock = MagicMock()
        ticker_mock.history.return_value = pd.DataFrame(columns=['Close'])
        with patch('finance_app.market_data.yf.Ticker', return_value=ticker_mock):
            self.assertIsNone(market_data.get_current_price('NOPE'))

    def test_current_prices_dedupes_and_batches(self):
        ticker_mock = MagicMock()
        ticker_mock.history.return_value = self._fake_history([10.0], ['2024-01-02'])
        with patch('finance_app.market_data.yf.Ticker', return_value=ticker_mock) as yf_ticker:
            prices = market_data.get_current_prices(['AAPL', 'aapl', 'MSFT'])

        # Set collapses the three inputs to two unique tickers.
        self.assertEqual(set(prices), {'AAPL', 'MSFT'})
        self.assertEqual(yf_ticker.call_count, 2)

    def test_price_on_date_falls_back_to_prior_trading_day(self):
        # Target date is a Sunday; yfinance returns Thursday + Friday and
        # the module must pick the latest close on or before the target.
        fake = self._fake_history([150.0, 152.0], ['2024-01-04', '2024-01-05'])
        ticker_mock = MagicMock()
        ticker_mock.history.return_value = fake
        with patch('finance_app.market_data.yf.Ticker', return_value=ticker_mock):
            price = market_data.get_price_on_date('AAPL', date(2024, 1, 7))
        self.assertEqual(price, Decimal('152.0'))
