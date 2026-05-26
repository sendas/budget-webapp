from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse


class MonthlyBudget(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "month", "year"], name="unique_budget_per_user_month")
        ]
        ordering = ["-year", "-month"]
        verbose_name = "Orçamento mensal"
        verbose_name_plural = "Orçamentos mensais"

    def __str__(self):
        return f"{self.owner} - {self.month:02d}/{self.year}"

    def get_absolute_url(self):
        return reverse("budget_detail", kwargs={"budget_id": self.pk})

    @property
    def fixed_total(self):
        return self.fixed_expenses.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def daily_total(self):
        return self.transactions.filter(kind=Transaction.Kind.DAILY).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def bongo_total(self):
        return self.transactions.filter(kind=Transaction.Kind.BONGO).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def spent_total(self):
        return self.fixed_total + self.daily_total + self.bongo_total

    @property
    def remaining_balance(self):
        return self.income - self.spent_total

    @property
    def savings_rate(self):
        if not self.income:
            return Decimal("0")
        return (self.remaining_balance / self.income) * Decimal("100")


class FixedExpense(models.Model):
    budget = models.ForeignKey(MonthlyBudget, on_delete=models.CASCADE, related_name="fixed_expenses")
    name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["name"]
        verbose_name = "Despesa fixa"
        verbose_name_plural = "Despesas fixas"

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class Kind(models.TextChoices):
        DAILY = "DAILY", "Despesa diaria"
        BONGO = "BONGO", "BONGO / extra"

    DAILY_CATEGORIES = [
        ("coffee", "Cafe"),
        ("drinks", "Bebidas"),
        ("food", "Comida"),
        ("shopping", "Compras"),
        ("entertainment", "Entretenimento"),
        ("transport", "Transporte"),
        ("health", "Saude"),
        ("other", "Outro"),
    ]
    BONGO_CATEGORIES = [
        ("fun", "Diversao"),
        ("clothes", "Roupa"),
        ("travel", "Viagens"),
        ("gifts", "Presentes"),
        ("repairs", "Reparacoes"),
        ("tech", "Tecnologia"),
        ("dining", "Restaurantes"),
        ("other", "Outro"),
    ]
    CATEGORY_CHOICES = [
        ("coffee", "Cafe"),
        ("drinks", "Bebidas"),
        ("food", "Comida"),
        ("shopping", "Compras"),
        ("entertainment", "Entretenimento"),
        ("transport", "Transporte"),
        ("health", "Saude"),
        ("other", "Outro"),
        ("fun", "Diversao"),
        ("clothes", "Roupa"),
        ("travel", "Viagens"),
        ("gifts", "Presentes"),
        ("repairs", "Reparacoes"),
        ("tech", "Tecnologia"),
        ("dining", "Restaurantes"),
    ]

    budget = models.ForeignKey(MonthlyBudget, on_delete=models.CASCADE, related_name="transactions")
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.DAILY)
    date = models.DateField()
    description = models.CharField(max_length=180)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="other")
    notes = models.CharField(max_length=240, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Movimento"
        verbose_name_plural = "Movimentos"

    def __str__(self):
        return f"{self.description} - {self.amount}"
