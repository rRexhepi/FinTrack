"""Sync migrations with the current model state.

The committed migrations (0001 + 0002) drifted out of sync with
`finance_app/models.py`:

* `Expense` gained `user` (FK), `db_index=True` on `date` and `category`,
  `blank=True` on `description`, and a `Meta.ordering` / `verbose_name_plural`;
* `Investment` gained `related_name='investments'` on its `user` FK and
  `Meta.ordering` / `verbose_name_plural`;
* `Budget` tightened `period.max_length` from 50 to 10, added
  `choices=...`, and picked up `related_name='budgets'` +
  `verbose_name_plural`;
* `Suggestion` is a whole new model that was never migrated.

Running a fresh `python manage.py migrate` before this migration lands
left the DB schema unable to satisfy any `Expense.objects.create(...)`
call that passed `user=...` — which CI surfaced by failing with
`column "user_id" of relation "finance_app_expense" does not exist`.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance_app', '0002_remove_investment_current_value_investment_ticker_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ---------- Expense ----------
        migrations.AddField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='expenses',
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='expense',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterModelOptions(
            name='expense',
            options={
                'ordering': ['-date'],
                'verbose_name': 'Expense',
                'verbose_name_plural': 'Expenses',
            },
        ),

        # ---------- Investment ----------
        migrations.AlterField(
            model_name='investment',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='investments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name='investment',
            options={
                'ordering': ['-date_invested'],
                'verbose_name': 'Investment',
                'verbose_name_plural': 'Investments',
            },
        ),

        # ---------- Budget ----------
        migrations.AlterField(
            model_name='budget',
            name='period',
            field=models.CharField(
                choices=[
                    ('Daily', 'Daily'),
                    ('Weekly', 'Weekly'),
                    ('Monthly', 'Monthly'),
                    ('Yearly', 'Yearly'),
                ],
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='budget',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='budgets',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name='budget',
            options={
                'verbose_name': 'Budget',
                'verbose_name_plural': 'Budgets',
            },
        ),

        # ---------- Suggestion (new) ----------
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='suggestions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Suggestion',
                'verbose_name_plural': 'Suggestions',
                'ordering': ['-created_at'],
            },
        ),
    ]
