from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Expense, Investment, Budget
from .serializers import (
    ExpenseSerializer,
    InvestmentSerializer,
    BudgetSerializer,
    SuggestionSerializer,
)

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class SuggestionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Analyze expenses over the last month
        last_month = timezone.now() - timedelta(days=30)
        expenses = Expense.objects.filter(user=request.user, date__gte=last_month)
        categories = {}
        for expense in expenses:
            categories.setdefault(expense.category, 0)
            categories[expense.category] += expense.amount

        suggestions = []
        for category, total in categories.items():
            if total > 500:
                suggestions.append(
                    f"You have spent ${total:.2f} on {category} in the last month. Consider reducing expenses in this category."
                )

        # Serialize the suggestions
        serializer = SuggestionSerializer({'suggestions': suggestions})
        return Response(serializer.data)