from datetime import date

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
    totals = {
        "income": sum((budget.income for budget in budgets), start=0),
        "spent": sum((budget.spent_total for budget in budgets), start=0),
        "remaining": sum((budget.remaining_balance for budget in budgets), start=0),
    }
    recent_transactions = Transaction.objects.filter(budget__owner=request.user).select_related("budget")[:8]
    return render(
        request,
        "finance/dashboard.html",
        {
            "budgets": budgets[:12],
            "current_budget": current_budget,
            "recent_transactions": recent_transactions,
            "totals": totals,
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
    kind_labels = get_kind_labels(language)
    transaction_rows = list(transactions[:60])
    for transaction in transaction_rows:
        transaction.kind_label = kind_labels.get(transaction.kind, transaction.get_kind_display())
        transaction.category_label = category_labels.get(transaction.category, transaction.get_category_display())
    return render(
        request,
        "finance/budget_detail.html",
        {
            "budget": budget,
            "fixed_expenses": budget.fixed_expenses.all(),
            "transactions": transaction_rows,
            "category_totals": category_totals,
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
