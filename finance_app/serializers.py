from rest_framework import serializers
from .models import Expense, Investment, Budget, Suggestion

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
    current_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Investment
        fields = ['id', 'user', 'name', 'ticker', 'amount_invested', 'date_invested', 'current_value']
        read_only_fields = ['id', 'user', 'current_value']

    def validate_amount_invested(self, value):
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be positive.")
        return value

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
