from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import FixedExpenseForm, LocalizedAuthenticationForm, MonthlyBudgetForm, SignupForm, TransactionForm
from .models import FixedExpense, MonthlyBudget, Transaction
from .preferences import LANGUAGES, THEMES, get_category_labels, get_kind_labels, get_language, get_text


DEFAULT_FIXED_EXPENSES = [
    "Renda / Casa",
    "Agua",
    "Eletricidade",
    "Internet",
    "Transporte",
    "Credito mensal",
    "Telefone",
]


def percent(value, total):
    if not total:
        return 0
    return max(0, min(100, round((value / total) * 100)))


def money_average(total, count):
    if not count:
        return Decimal("0")
    return total / Decimal(count)


def signup(request):
    language = get_language(request)
    if request.method == "POST":
        form = SignupForm(request.POST, language=language)
        if form.is_valid():
            form.save()
            return redirect("pending_approval")
    else:
        form = SignupForm(language=language)
    return render(request, "registration/signup.html", {"form": form})


def login_view(request):
    language = get_language(request)
    if request.method == "POST":
        form = LocalizedAuthenticationForm(request, data=request.POST, language=language)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = LocalizedAuthenticationForm(request, language=language)
    return render(request, "registration/login.html", {"form": form})


def preferences_update(request):
    if request.method == "POST":
        language = request.POST.get("language")
        theme = request.POST.get("theme")
        if language in LANGUAGES:
            request.session["language"] = language
        if theme in THEMES:
            request.session["theme"] = theme
    return HttpResponseRedirect(request.POST.get("next") or reverse("dashboard"))


def pending_approval(request):
    return render(request, "registration/pending_approval.html")


@login_required
def dashboard(request):
    budgets = MonthlyBudget.objects.filter(owner=request.user)
    current_budget = budgets.first()
    budget_list = list(budgets[:12])
    totals = {
        "income": sum((budget.income for budget in budget_list), start=Decimal("0")),
        "spent": sum((budget.spent_total for budget in budget_list), start=Decimal("0")),
        "remaining": sum((budget.remaining_balance for budget in budget_list), start=Decimal("0")),
    }
    trend_source = list(reversed(budget_list[:6]))
    max_trend_spent = max([budget.spent_total for budget in trend_source] or [Decimal("0")])
    monthly_trend = [
        {
            "label": f"{budget.month:02d}/{str(budget.year)[-2:]}",
            "spent": budget.spent_total,
            "income": budget.income,
            "width": percent(budget.spent_total, max_trend_spent),
        }
        for budget in trend_source
    ]
    spend_count = len([budget for budget in budget_list if budget.spent_total])
    savings_rate = percent(totals["remaining"], totals["income"])
    expense_ratio = percent(totals["spent"], totals["income"])
    overview_stats = {
        "average_spend": money_average(totals["spent"], spend_count),
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
    }
    expense_mix = [
        {"label": get_text(request)["spent"], "value": totals["spent"], "width": expense_ratio},
        {"label": get_text(request)["remaining"], "value": totals["remaining"], "width": max(0, 100 - expense_ratio)},
    ]
    recent_transactions = Transaction.objects.filter(budget__owner=request.user).select_related("budget")[:8]
    return render(
        request,
        "finance/dashboard.html",
        {
            "budgets": budget_list,
            "current_budget": current_budget,
            "recent_transactions": recent_transactions,
            "totals": totals,
            "monthly_trend": monthly_trend,
            "overview_stats": overview_stats,
            "expense_mix": expense_mix,
        },
    )


@login_required
def budget_create(request):
    language = get_language(request)
    text = get_text(request)
    initial = {"month": date.today().month, "year": date.today().year}
    if request.method == "POST":
        form = MonthlyBudgetForm(request.POST, language=language)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.owner = request.user
            budget.save()
            for name in DEFAULT_FIXED_EXPENSES:
                FixedExpense.objects.create(budget=budget, name=name, amount=0)
            messages.success(request, text["budget_created"])
            return redirect(budget)
    else:
        form = MonthlyBudgetForm(initial=initial, language=language)
    return render(request, "finance/form_page.html", {"form": form, "title": text["new_budget"], "button_label": text["create"]})


@login_required
def budget_detail(request, budget_id):
    language = get_language(request)
    budget = get_object_or_404(MonthlyBudget, pk=budget_id, owner=request.user)
    transactions = budget.transactions.all()
    category_totals = (
        transactions.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:6]
    )
    category_labels = get_category_labels(language)
    category_totals = [
        {"category": category_labels.get(item["category"], item["category"]), "total": item["total"]}
        for item in category_totals
    ]
    max_category_total = max([item["total"] for item in category_totals] or [Decimal("0")])
    for item in category_totals:
        item["width"] = percent(item["total"], max_category_total)
        item["share"] = percent(item["total"], budget.spent_total)
    kind_labels = get_kind_labels(language)
    transaction_rows = list(transactions[:60])
    for transaction in transaction_rows:
        transaction.kind_label = kind_labels.get(transaction.kind, transaction.get_kind_display())
        transaction.category_label = category_labels.get(transaction.category, transaction.get_category_display())
    text = get_text(request)
    expense_mix = [
        {"label": text["fixed"], "value": budget.fixed_total, "width": percent(budget.fixed_total, budget.spent_total)},
        {"label": text["daily"], "value": budget.daily_total, "width": percent(budget.daily_total, budget.spent_total)},
        {"label": "BONGO", "value": budget.bongo_total, "width": percent(budget.bongo_total, budget.spent_total)},
    ]
    transaction_count = transactions.count()
    budget_stats = {
        "savings_rate": percent(budget.remaining_balance, budget.income),
        "expense_ratio": percent(budget.spent_total, budget.income),
        "transaction_count": transaction_count,
        "average_spend": money_average(budget.spent_total, transaction_count + budget.fixed_expenses.count()),
        "largest_category": category_totals[0]["category"] if category_totals else "-",
    }
    return render(
        request,
        "finance/budget_detail.html",
        {
            "budget": budget,
            "fixed_expenses": budget.fixed_expenses.all(),
            "transactions": transaction_rows,
            "category_totals": category_totals,
            "expense_mix": expense_mix,
            "budget_stats": budget_stats,
        },
    )


@login_required
def fixed_expense_create(request, budget_id):
    language = get_language(request)
    text = get_text(request)
    budget = get_object_or_404(MonthlyBudget, pk=budget_id, owner=request.user)
    if request.method == "POST":
        form = FixedExpenseForm(request.POST, language=language)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.save()
            messages.success(request, text["fixed_added"])
            return redirect(budget)
    else:
        form = FixedExpenseForm(language=language)
    return render(request, "finance/form_page.html", {"form": form, "title": text["new_fixed_expense"], "button_label": text["save"]})


@login_required
def transaction_create(request, budget_id):
    language = get_language(request)
    text = get_text(request)
    budget = get_object_or_404(MonthlyBudget, pk=budget_id, owner=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, language=language)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.budget = budget
            transaction.save()
            messages.success(request, text["transaction_added"])
            return redirect(budget)
    else:
        form = TransactionForm(initial={"date": date.today()}, language=language)
    return render(request, "finance/form_page.html", {"form": form, "title": text["new_transaction"], "button_label": text["register"]})


@login_required
def fixed_expense_delete(request, expense_id):
    expense = get_object_or_404(FixedExpense, pk=expense_id, budget__owner=request.user)
    budget = expense.budget
    if request.method == "POST":
        expense.delete()
        messages.success(request, get_text(request)["fixed_removed"])
    return redirect(budget)


@login_required
def transaction_delete(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, budget__owner=request.user)
    budget = transaction.budget
    if request.method == "POST":
        transaction.delete()
        messages.success(request, get_text(request)["transaction_removed"])
    return redirect(budget)
