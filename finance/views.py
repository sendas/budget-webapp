from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FixedExpenseForm, MonthlyBudgetForm, SignupForm, TransactionForm
from .models import FixedExpense, MonthlyBudget, Transaction


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
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("pending_approval")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


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
    initial = {"month": date.today().month, "year": date.today().year}
    if request.method == "POST":
        form = MonthlyBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.owner = request.user
            budget.save()
            for name in DEFAULT_FIXED_EXPENSES:
                FixedExpense.objects.create(budget=budget, name=name, amount=0)
            messages.success(request, "Orcamento mensal criado.")
            return redirect(budget)
    else:
        form = MonthlyBudgetForm(initial=initial)
    return render(request, "finance/form_page.html", {"form": form, "title": "Novo orcamento", "button_label": "Criar"})


@login_required
def budget_detail(request, budget_id):
    budget = get_object_or_404(MonthlyBudget, pk=budget_id, owner=request.user)
    transactions = budget.transactions.all()
    category_totals = (
        transactions.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:6]
    )
    category_labels = dict(Transaction.CATEGORY_CHOICES)
    category_totals = [
        {"category": category_labels.get(item["category"], item["category"]), "total": item["total"]}
        for item in category_totals
    ]
    return render(
        request,
        "finance/budget_detail.html",
        {
            "budget": budget,
            "fixed_expenses": budget.fixed_expenses.all(),
            "transactions": transactions[:60],
            "category_totals": category_totals,
        },
    )


@login_required
def fixed_expense_create(request, budget_id):
    budget = get_object_or_404(MonthlyBudget, pk=budget_id, owner=request.user)
    if request.method == "POST":
        form = FixedExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.save()
            messages.success(request, "Despesa fixa adicionada.")
            return redirect(budget)
    else:
        form = FixedExpenseForm()
    return render(request, "finance/form_page.html", {"form": form, "title": "Nova despesa fixa", "button_label": "Guardar"})


@login_required
def transaction_create(request, budget_id):
    budget = get_object_or_404(MonthlyBudget, pk=budget_id, owner=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.budget = budget
            transaction.save()
            messages.success(request, "Movimento registado.")
            return redirect(budget)
    else:
        form = TransactionForm(initial={"date": date.today()})
    return render(request, "finance/form_page.html", {"form": form, "title": "Novo movimento", "button_label": "Registar"})


@login_required
def fixed_expense_delete(request, expense_id):
    expense = get_object_or_404(FixedExpense, pk=expense_id, budget__owner=request.user)
    budget = expense.budget
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Despesa fixa removida.")
    return redirect(budget)


@login_required
def transaction_delete(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, budget__owner=request.user)
    budget = transaction.budget
    if request.method == "POST":
        transaction.delete()
        messages.success(request, "Movimento removido.")
    return redirect(budget)
