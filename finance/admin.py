from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import FixedExpense, MonthlyBudget, Transaction

admin.site.site_header = "financebros admin"
admin.site.site_title = "financebros"
admin.site.index_title = "Gestão financeira"

admin.site.unregister(User)


@admin.register(User)
class FinancebrosUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informação pessoal"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Aprovação e acesso"),
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups"),
                "description": _("Para aprovar um utilizador normal, marque apenas Ativo. Status de equipa dá acesso à administração."),
            },
        ),
        (_("Datas importantes"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "is_active"),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    filter_horizontal = ("groups",)


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
