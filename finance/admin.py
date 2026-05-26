from django.contrib import admin

from .models import FixedExpense, MonthlyBudget, Transaction

admin.site.site_header = "financebros admin"
admin.site.site_title = "financebros"
admin.site.index_title = "Gestão financeira"


@admin.register(MonthlyBudget)
class MonthlyBudgetAdmin(admin.ModelAdmin):
    list_display = ("owner", "month", "year", "income", "spent_total", "remaining_balance", "created_at")
    list_filter = ("year", "month")
    search_fields = ("owner__username", "owner__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(FixedExpense)
class FixedExpenseAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "budget")
    list_filter = ("budget__year", "budget__month")
    search_fields = ("name", "budget__owner__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "description", "kind", "category", "amount", "budget")
    list_filter = ("kind", "category", "date")
    search_fields = ("description", "notes", "budget__owner__username")
    date_hierarchy = "date"
