from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Expense, Investment, Budget, Suggestion
from .serializers import (
    ExpenseSerializer,
    InvestmentSerializer,
    BudgetSerializer,
    SuggestionSerializer,
)
from rest_framework.decorators import action

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user).order_by('-date_invested')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Suggestion.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def generate(self, request):
        # Analyze expenses over the last month
        last_month = timezone.now() - timedelta(days=30)
        expenses = Expense.objects.filter(user=request.user, date__gte=last_month)
        categories = {}
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
                    f"You have spent ${total:.2f} on {category} in the last month. Consider reducing expenses in this category."
                )

        # Save suggestions to the database
        for message in suggestions:
            Suggestion.objects.create(user=request.user, message=message)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
