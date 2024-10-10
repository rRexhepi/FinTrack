from rest_framework import serializers
from .models import Expense, Investment, Budget

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('user',)
        
class SuggestionSerializer(serializers.Serializer):
    suggestions = serializers.ListField(
        child=serializers.CharField()
    )

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class InvestmentSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = '__all__'
        read_only_fields = ('user',)

    def get_current_value(self, obj):
        return obj.current_value