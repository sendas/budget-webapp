from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import FixedExpense, MonthlyBudget, Transaction


class SignupForm(UserCreationForm):
    username = forms.CharField(label="Utilizador")
    email = forms.EmailField(label="Email", required=True)
    password1 = forms.CharField(
        label="Palavra-passe",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Usa pelo menos 8 caracteres e evita palavras-passe comuns ou totalmente numericas.",
    )
    password2 = forms.CharField(
        label="Confirmacao da palavra-passe",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Repete a palavra-passe para confirmacao.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        if commit:
            user.save()
        return user


class MonthlyBudgetForm(forms.ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = ("month", "year", "income")
        labels = {"month": "Mes", "year": "Ano", "income": "Rendimento"}
        widgets = {
            "month": forms.NumberInput(attrs={"min": 1, "max": 12}),
            "year": forms.NumberInput(attrs={"min": 2020, "max": 2100}),
        }


class FixedExpenseForm(forms.ModelForm):
    class Meta:
        model = FixedExpense
        fields = ("name", "amount")
        labels = {"name": "Nome", "amount": "Valor"}


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ("kind", "date", "description", "category", "notes", "amount")
        labels = {
            "kind": "Tipo",
            "date": "Data",
            "description": "Descricao",
            "category": "Categoria",
            "notes": "Notas",
            "amount": "Valor",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(attrs={"placeholder": "Opcional"}),
        }
