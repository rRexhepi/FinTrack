from datetime import date, timedelta

from django.db.models import Min, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import market_data
from .models import Budget, Expense, Investment, Suggestion
from .serializers import (
    BudgetSerializer,
    ExpenseSerializer,
    InvestmentSerializer,
    SuggestionSerializer,
)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        # SQL-side aggregate for the dashboard pie chart. Returns one row
        # per category instead of the paginated expense list, which the
        # chart was misusing: at PAGE_SIZE=10 it only ever saw the first
        # page and under-reported categories with rows further back.
        rows = (
            Expense.objects
            .filter(user=request.user)
            .values('category')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        return Response([
            {'category': row['category'], 'total': float(row['total'])}
            for row in rows
        ])


class InvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user).order_by('-date_invested')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def allocation(self, request):
        # Cost-basis allocation by ticker — drives the dashboard donut.
        # Grouping by ticker (not by row) so a user with two AAPL buys
        # shows as one slice; `Min('name')` picks a stable display name.
        rows = (
            Investment.objects
            .filter(user=request.user)
            .values('ticker')
            .annotate(total=Sum('amount_invested'), name=Min('name'))
            .order_by('-total')
        )
        return Response([
            {
                'ticker': row['ticker'],
                'name': row['name'],
                'total': float(row['total']),
            }
            for row in rows
        ])

    def list(self, request, *args, **kwargs):
        # Batch-fetch current prices for every ticker on the current page
        # so the serializer doesn't hit yfinance once per investment. This
        # is the whole point of the refactor that extracted yfinance out
        # of `Investment`'s model properties.
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        objects = page if page is not None else list(queryset)

        context = self.get_serializer_context()
        tickers = {obj.ticker for obj in objects if obj.ticker}
        if tickers:
            context['current_prices'] = market_data.get_current_prices(tickers)

        serializer = self.get_serializer(objects, many=True, context=context)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


def _period_start(period: str, today: date) -> date:
    """First day of the current budget window for a given cadence.

    Keeping this module-level (not a method) so it's easy to unit-test
    without standing up a Budget + user.
    """
    if period == 'Daily':
        return today
    if period == 'Weekly':
        return today - timedelta(days=today.weekday())  # Monday
    if period == 'Yearly':
        return today.replace(month=1, day=1)
    # Monthly is the fallback and the common case.
    return today.replace(day=1)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def progress(self, request):
        # For each budget, how much has the user spent in that category
        # during the current period. Drives the dashboard progress bars.
        # The "current period" depends on the budget's cadence; see
        # `_period_start`.
        today = timezone.now().date()
        out = []
        for budget in self.get_queryset():
            window_start = _period_start(budget.period, today)
            spent = (
                Expense.objects
                .filter(
                    user=request.user,
                    category=budget.category,
                    date__gte=window_start,
                    date__lte=today,
                )
                .aggregate(total=Sum('amount'))['total']
            ) or 0
            out.append({
                'id': budget.id,
                'category': budget.category,
                'period': budget.period,
                'amount': float(budget.amount),
                'spent': float(spent),
                'window_start': window_start.isoformat(),
            })
        return Response(out)


class SuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Suggestion.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def generate(self, request):
        # Analyse expenses over the last 30 days and emit a suggestion
        # per category where the user is over budget or has spent > $500.
        last_month = timezone.now() - timedelta(days=30)
        expenses = Expense.objects.filter(user=request.user, date__gte=last_month)
        categories: dict[str, float] = {}
        for expense in expenses:
            categories.setdefault(expense.category, 0)
            categories[expense.category] += expense.amount

        suggestions = []
        for category, total in categories.items():
            budget = Budget.objects.filter(user=request.user, category=category).first()
            if budget and total > budget.amount:
                suggestions.append(
                    f"You have exceeded your {category} budget by ${total - budget.amount:.2f}."
                )
            elif total > 500:
                suggestions.append(
                    f"You have spent ${total:.2f} on {category} in the last month. "
                    "Consider reducing expenses in this category."
                )

        for message in suggestions:
            Suggestion.objects.create(user=request.user, message=message)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
