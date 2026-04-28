"""Seed a demo user with realistic fake data for public deployments.

Idempotent: if the demo user already has records, exits without touching
them. Pass `--force` to wipe-and-reseed. Safe to leave in the build
command on a public-demo deployment.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from finance_app.models import Budget, Expense, Investment, Suggestion


class Command(BaseCommand):
    help = 'Seed a demo user with realistic fake finance data.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo')
        parser.add_argument('--password', default='demopass123')
        parser.add_argument(
            '--force',
            action='store_true',
            help="Wipe the demo user's existing data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        username = opts['username']
        password = opts['password']
        force = opts['force']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'."))
        elif force:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['password', 'is_staff', 'is_superuser'])
            Expense.objects.filter(user=user).delete()
            Investment.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            Suggestion.objects.filter(user=user).delete()
            self.stdout.write(
                self.style.WARNING(f"Reset '{username}' and wiped their data.")
            )
        elif user.expenses.exists() or user.investments.exists():
            self.stdout.write(
                self.style.NOTICE(
                    f"User '{username}' already has data. Pass --force to re-seed."
                )
            )
            return

        today = date.today()

        expenses = [
            ('Groceries',      '128.47', 1,  'Weekly shop, produce + pantry'),
            ('Dining Out',     '42.10',  2,  'Ramen with M.'),
            ('Transportation', '52.00',  3,  'Gas'),
            ('Groceries',      '76.82',  6,  'Costco run'),
            ('Entertainment',  '18.99',  8,  'Streaming subscription'),
            ('Utilities',      '142.30', 10, 'Electric bill'),
            ('Dining Out',     '67.50',  12, 'Birthday dinner'),
            ('Groceries',      '94.15',  15, 'Trader Joe\'s'),
            ('Transportation', '22.00',  17, 'Uber to airport'),
            ('Entertainment',  '48.00',  21, 'Concert tickets'),
            ('Rent',           '1450.00', 23, 'Monthly rent'),
            ('Utilities',      '68.40',  25, 'Internet + phone'),
            ('Groceries',      '112.00', 29, 'Monthly staples'),
            ('Dining Out',     '28.75',  33, 'Lunch'),
        ]
        Expense.objects.bulk_create([
            Expense(
                user=user,
                category=cat,
                amount=Decimal(amt),
                date=today - timedelta(days=days_ago),
                description=desc,
            )
            for cat, amt, days_ago, desc in expenses
        ])

        investments = [
            ('Apple Inc.',            'AAPL',  '1850.00', 120),
            ('Microsoft Corp.',       'MSFT',  '2400.00', 90),
            ('Alphabet (Google)',     'GOOGL', '1200.00', 60),
            ('Vanguard Total Market', 'VTI',   '3500.00', 200),
            ('NVIDIA Corp.',          'NVDA',  '2100.00', 45),
        ]
        Investment.objects.bulk_create([
            Investment(
                user=user,
                name=name,
                ticker=ticker,
                amount_invested=Decimal(amount),
                date_invested=today - timedelta(days=days_ago),
            )
            for name, ticker, amount, days_ago in investments
        ])

        budgets = [
            ('Groceries',      '500.00', 'Monthly'),
            ('Dining Out',     '200.00', 'Monthly'),
            ('Entertainment',  '150.00', 'Monthly'),
            ('Transportation', '250.00', 'Monthly'),
        ]
        Budget.objects.bulk_create([
            Budget(user=user, category=cat, amount=Decimal(amt), period=period)
            for cat, amt, period in budgets
        ])

        suggestion_messages = [
            "Groceries is your largest recurring category. Batching a weekend "
            "haul rather than topping up mid-week tends to cut the total.",
            "Dining Out is pacing close to its budget. Not alarming yet, but "
            "worth keeping an eye on before weekend plans land.",
            "Entertainment is comfortably under budget. You've got headroom "
            "for a night out without denting the rest of the month.",
        ]
        Suggestion.objects.bulk_create([
            Suggestion(user=user, message=msg) for msg in suggestion_messages
        ])

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(expenses)} expenses, {len(investments)} investments, "
            f"{len(budgets)} budgets, {len(suggestion_messages)} suggestions "
            f"for '{username}'."
        ))
