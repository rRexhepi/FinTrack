from django.contrib import admin

from .models import Budget, Expense, Investment, Suggestion


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'category', 'amount')
    list_filter = ('category', 'date')
    search_fields = ('user__username', 'category', 'description')


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'ticker', 'amount_invested', 'date_invested')
    list_filter = ('ticker',)
    search_fields = ('user__username', 'name', 'ticker')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'period')
    list_filter = ('period', 'category')
    search_fields = ('user__username', 'category')


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
