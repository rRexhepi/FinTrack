# finance_app/tests.py

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
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


class ExpenseByCategoryTest(TestCase):
    """The aggregation endpoint the dashboard chart uses."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='chartuser', password='x')
        self.client.force_authenticate(user=self.user)

        # 12 expenses across 3 categories — deliberately more than the
        # default PAGE_SIZE (10) so a broken implementation that read the
        # paginated list would miss rows on page 2.
        rows = [
            ('Groceries',     '100.00'),
            ('Groceries',     '50.00'),
            ('Groceries',     '25.00'),
            ('Dining Out',    '40.00'),
            ('Dining Out',    '60.00'),
            ('Transportation', '15.00'),
            ('Transportation', '35.00'),
            ('Groceries',     '10.00'),
            ('Dining Out',    '20.00'),
            ('Groceries',     '5.00'),
            ('Transportation', '50.00'),
            ('Groceries',     '75.00'),
        ]
        for i, (cat, amt) in enumerate(rows):
            Expense.objects.create(
                user=self.user,
                date=date(2024, 1, 1),
                category=cat,
                amount=Decimal(amt),
            )

    def test_totals_span_entire_expense_history(self):
        resp = self.client.get('/api/expenses/by-category/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        totals = {row['category']: row['total'] for row in resp.json()}
        # 265 total for Groceries across 6 rows — spanning the paginated
        # page boundary is the whole point of this endpoint.
        self.assertEqual(totals, {
            'Groceries': 265.0,
            'Dining Out': 120.0,
            'Transportation': 100.0,
        })

    def test_scoped_to_requesting_user(self):
        other = User.objects.create_user(username='someone_else', password='x')
        Expense.objects.create(
            user=other, date=date(2024, 1, 1),
            category='Groceries', amount=Decimal('9999.00'),
        )
        resp = self.client.get('/api/expenses/by-category/')
        totals = {row['category']: row['total'] for row in resp.json()}
        self.assertEqual(totals['Groceries'], 265.0)

    def test_requires_auth(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/expenses/by-category/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class InvestmentAllocationTest(TestCase):
    """`/api/investments/allocation/` — cost-basis by ticker for the donut."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='allocuser', password='x')
        self.client.force_authenticate(user=self.user)

    def test_groups_two_buys_of_same_ticker(self):
        # Two AAPL positions and one MSFT. The chart wants one slice per
        # ticker, not one per row.
        Investment.objects.create(
            user=self.user, name='Apple Inc.', ticker='AAPL',
            amount_invested=Decimal('1000.00'), date_invested=date(2024, 1, 1),
        )
        Investment.objects.create(
            user=self.user, name='Apple Inc.', ticker='AAPL',
            amount_invested=Decimal('500.00'), date_invested=date(2024, 6, 1),
        )
        Investment.objects.create(
            user=self.user, name='Microsoft Corp.', ticker='MSFT',
            amount_invested=Decimal('750.00'), date_invested=date(2024, 3, 1),
        )

        resp = self.client.get('/api/investments/allocation/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        by_ticker = {row['ticker']: row for row in resp.json()}
        self.assertEqual(len(by_ticker), 2)
        self.assertEqual(by_ticker['AAPL']['total'], 1500.0)
        self.assertEqual(by_ticker['MSFT']['total'], 750.0)

    def test_scoped_to_requesting_user(self):
        Investment.objects.create(
            user=self.user, name='Apple', ticker='AAPL',
            amount_invested=Decimal('100.00'), date_invested=date(2024, 1, 1),
        )
        other = User.objects.create_user(username='not_me', password='x')
        Investment.objects.create(
            user=other, name='Apple', ticker='AAPL',
            amount_invested=Decimal('9999.00'), date_invested=date(2024, 1, 1),
        )
        resp = self.client.get('/api/investments/allocation/')
        self.assertEqual(resp.json()[0]['total'], 100.0)

    def test_requires_auth(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/investments/allocation/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class BudgetProgressTest(TestCase):
    """`/api/budgets/progress/` — spent-this-period per budget."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='budgetuser2', password='x')
        self.client.force_authenticate(user=self.user)

    def test_monthly_budget_sums_month_to_date(self):
        today = timezone.now().date()
        first_of_month = today.replace(day=1)

        Budget.objects.create(
            user=self.user, category='Groceries',
            amount=Decimal('500.00'), period='Monthly',
        )
        # In the current month — counted.
        Expense.objects.create(
            user=self.user, date=first_of_month,
            category='Groceries', amount=Decimal('120.00'),
        )
        Expense.objects.create(
            user=self.user, date=today,
            category='Groceries', amount=Decimal('30.00'),
        )
        # Last month — excluded.
        last_month = (first_of_month - timedelta(days=1))
        Expense.objects.create(
            user=self.user, date=last_month,
            category='Groceries', amount=Decimal('9999.00'),
        )
        # Different category — excluded.
        Expense.objects.create(
            user=self.user, date=today,
            category='Dining Out', amount=Decimal('40.00'),
        )

        resp = self.client.get('/api/budgets/progress/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        rows = resp.json()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['category'], 'Groceries')
        self.assertEqual(rows[0]['amount'], 500.0)
        self.assertEqual(rows[0]['spent'], 150.0)
        self.assertEqual(rows[0]['window_start'], first_of_month.isoformat())

    def test_budget_with_no_matching_expenses_reports_zero(self):
        Budget.objects.create(
            user=self.user, category='Travel',
            amount=Decimal('300.00'), period='Monthly',
        )
        resp = self.client.get('/api/budgets/progress/')
        self.assertEqual(resp.json()[0]['spent'], 0)

    def test_requires_auth(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/budgets/progress/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PeriodStartTest(TestCase):
    """Unit test the budget-period helper; cheap, no DB."""

    def test_daily(self):
        from finance_app.views import _period_start
        d = date(2024, 3, 15)
        self.assertEqual(_period_start('Daily', d), d)

    def test_weekly_returns_monday(self):
        from finance_app.views import _period_start
        # 2024-03-15 is a Friday → Monday is 2024-03-11.
        self.assertEqual(_period_start('Weekly', date(2024, 3, 15)), date(2024, 3, 11))

    def test_monthly_returns_first(self):
        from finance_app.views import _period_start
        self.assertEqual(_period_start('Monthly', date(2024, 3, 15)), date(2024, 3, 1))

    def test_yearly_returns_jan_1(self):
        from finance_app.views import _period_start
        self.assertEqual(_period_start('Yearly', date(2024, 3, 15)), date(2024, 1, 1))


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

    def test_failed_lookup_is_cached(self):
        """A failure caches `None` so we don't retry yfinance on every
        page load when Yahoo's rate-limiting us."""
        ticker_mock = MagicMock()
        ticker_mock.history.side_effect = RuntimeError('rate limited')
        with patch('finance_app.market_data.yf.Ticker', return_value=ticker_mock) as yf_ticker:
            first = market_data.get_current_price('AAPL')
            second = market_data.get_current_price('AAPL')
        self.assertIsNone(first)
        self.assertIsNone(second)
        # Single yfinance hit, not two.
        self.assertEqual(yf_ticker.call_count, 1)

    def test_empty_frame_is_cached_too(self):
        """Same negative-cache story for the 'possibly delisted' path."""
        ticker_mock = MagicMock()
        ticker_mock.history.return_value = pd.DataFrame(columns=['Close'])
        with patch('finance_app.market_data.yf.Ticker', return_value=ticker_mock) as yf_ticker:
            market_data.get_current_price('NOPE')
            market_data.get_current_price('NOPE')
        self.assertEqual(yf_ticker.call_count, 1)

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


class InvestmentAPITests(TestCase):
    """Viewset + serializer integration tests for the yfinance refactor."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username='investor', password='pw')
        self.client.force_authenticate(user=self.user)

    def _make(self, *, ticker='AAPL', amount=1000, user=None):
        return Investment.objects.create(
            user=user or self.user,
            name=ticker,
            ticker=ticker,
            amount_invested=amount,
            date_invested=date(2024, 1, 2),
        )

    def test_list_batches_current_price_fetches(self):
        # Three investments → the viewset should hit `get_current_prices`
        # exactly once, with a deduped ticker set. Before the refactor this
        # was 6 synchronous yfinance calls (2 per instance).
        self._make(ticker='AAPL')
        self._make(ticker='MSFT')
        self._make(ticker='GOOG')

        with patch('finance_app.views.market_data.get_current_prices') as mock_batch, \
             patch(
                 'finance_app.serializers.market_data.get_price_on_date',
                 return_value=Decimal('100'),
             ):
            mock_batch.return_value = {
                'AAPL': Decimal('200'),
                'MSFT': Decimal('300'),
                'GOOG': Decimal('400'),
            }
            response = self.client.get(reverse('investment-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_batch.assert_called_once()
        passed_tickers = set(mock_batch.call_args.args[0])
        self.assertEqual(passed_tickers, {'AAPL', 'MSFT', 'GOOG'})

    def test_list_exposes_current_value_from_batch(self):
        self._make(ticker='AAPL', amount=1000)

        with patch(
            'finance_app.views.market_data.get_current_prices',
            return_value={'AAPL': Decimal('200')},
        ), patch(
            'finance_app.serializers.market_data.get_price_on_date',
            return_value=Decimal('100'),
        ):
            response = self.client.get(reverse('investment-list'))

        row = response.json()['results'][0]
        # 1000 purchased / 100 per share = 10 shares; 10 × 200 = 2000.
        self.assertAlmostEqual(row['current_value'], 2000.0)

    def test_list_returns_null_current_value_when_ticker_unresolvable(self):
        self._make(ticker='BOGUS')
        with patch(
            'finance_app.views.market_data.get_current_prices',
            return_value={},
        ), patch(
            'finance_app.serializers.market_data.get_current_price',
            return_value=None,
        ):
            response = self.client.get(reverse('investment-list'))
        row = response.json()['results'][0]
        self.assertIsNone(row['current_value'])

    def test_list_scopes_to_authenticated_user(self):
        other = User.objects.create_user(username='someoneelse', password='pw')
        self._make(ticker='META', user=other)
        self._make(ticker='AAPL')

        with patch(
            'finance_app.views.market_data.get_current_prices',
            return_value={},
        ), patch(
            'finance_app.serializers.market_data.get_current_price',
            return_value=None,
        ):
            response = self.client.get(reverse('investment-list'))

        tickers = [r['ticker'] for r in response.json()['results']]
        self.assertEqual(tickers, ['AAPL'])

    def test_create_rejects_non_positive_amount(self):
        response = self.client.post(
            reverse('investment-list'),
            {
                'name': 'Apple',
                'ticker': 'AAPL',
                'amount_invested': 0,
                'date_invested': '2024-01-02',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount_invested', response.json())


class JWTAuthTests(TestCase):
    """SimpleJWT issue + consume round-trip."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='jwtuser', password='jwtpass')

    def test_obtain_token_and_call_protected_endpoint(self):
        resp = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'jwtpass'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        body = resp.json()
        self.assertIn('access', body)
        self.assertIn('refresh', body)

        # Use the access token to hit a protected endpoint — no session,
        # just the Authorization header, the way a real SPA would.
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {body['access']}")
        protected = self.client.get(reverse('expense-list'))
        self.assertEqual(protected.status_code, status.HTTP_200_OK)

    def test_refresh_token_issues_new_access(self):
        tokens = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'jwtpass'},
            format='json',
        ).json()

        refreshed = self.client.post(
            reverse('token_refresh'),
            {'refresh': tokens['refresh']},
            format='json',
        )
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        self.assertIn('access', refreshed.json())

    def test_bad_credentials_rejected(self):
        resp = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class SeedDemoCommandTest(TestCase):
    """`seed_demo` creates a user + data on first run and is idempotent."""

    def _run(self, **opts):
        from django.core.management import call_command
        call_command('seed_demo', **opts)

    def test_seeds_user_and_counts(self):
        self._run()
        demo = User.objects.get(username='demo')
        self.assertTrue(demo.is_superuser)
        self.assertTrue(demo.check_password('demopass123'))
        self.assertEqual(demo.expenses.count(), 14)
        self.assertEqual(demo.investments.count(), 5)
        self.assertEqual(demo.budgets.count(), 4)
        self.assertEqual(demo.suggestions.count(), 3)

    def test_rerun_is_noop(self):
        self._run()
        self._run()  # second call should skip
        self.assertEqual(User.objects.filter(username='demo').count(), 1)
        self.assertEqual(
            Expense.objects.filter(user__username='demo').count(), 14
        )

    def test_force_wipes_and_reseeds(self):
        self._run()
        Expense.objects.filter(user__username='demo').update(amount=Decimal('1'))
        self._run(force=True)
        # `force` path reseeds with original amounts, no 1.00 stragglers.
        self.assertFalse(
            Expense.objects.filter(user__username='demo', amount=Decimal('1')).exists()
        )
        self.assertEqual(
            Expense.objects.filter(user__username='demo').count(), 14
        )
