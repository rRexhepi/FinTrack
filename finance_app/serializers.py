from decimal import Decimal

from rest_framework import serializers

from . import market_data
from .models import Budget, Expense, Investment, Suggestion


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'user', 'date', 'category', 'amount', 'description']
        read_only_fields = ['id', 'user']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class InvestmentSerializer(serializers.ModelSerializer):
    # Computed from yfinance via `market_data`. List endpoints pre-warm a
    # batch via serializer context (see InvestmentViewSet.list). Detail
    # endpoints fall back to the cached single-ticker lookup. `None` here
    # means yfinance couldn't resolve the ticker, so the frontend should
    # render a dash rather than a zero.
    current_value = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = [
            'id', 'user', 'name', 'ticker', 'amount_invested',
            'date_invested', 'current_value',
        ]
        read_only_fields = ['id', 'user', 'current_value']

    def validate_amount_invested(self, value):
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be positive.")
        return value

    def get_current_value(self, obj: Investment) -> float | None:
        prices = self.context.get('current_prices') or {}
        current = prices.get(obj.ticker.upper()) if obj.ticker else None
        if current is None:
            current = market_data.get_current_price(obj.ticker)
        if current is None:
            return None
        purchase = market_data.get_price_on_date(obj.ticker, obj.date_invested)
        if not purchase:
            return None
        shares = Decimal(obj.amount_invested) / purchase
        return float(current * shares)


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'amount', 'period']
        read_only_fields = ['id', 'user']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be positive.")
        return value


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'user', 'message', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
