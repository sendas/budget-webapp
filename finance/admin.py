from django.contrib import admin

from .models import FixedExpense, MonthlyBudget, Transaction


@admin.register(MonthlyBudget)
class MonthlyBudgetAdmin(admin.ModelAdmin):
    list_display = ("owner", "month", "year", "income", "created_at")
    list_filter = ("year", "month")
    search_fields = ("owner__username", "owner__email")


@admin.register(FixedExpense)
class FixedExpenseAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "budget")
    search_fields = ("name", "budget__owner__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "description", "kind", "category", "amount", "budget")
    list_filter = ("kind", "category", "date")
    search_fields = ("description", "notes", "budget__owner__username")
