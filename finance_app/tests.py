# finance_app/tests.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Expense, Investment, Budget
from rest_framework.test import APIClient
from rest_framework import status

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
