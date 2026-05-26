from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import FixedExpense, MonthlyBudget, Transaction
from .preferences import get_category_labels, get_form_text, get_kind_labels


class SignupForm(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField(label="Email", required=True)
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, language="pt", **kwargs):
        super().__init__(*args, **kwargs)
        text = get_form_text(language)
        self.fields["username"].label = text["username"]
        self.fields["password1"].label = text["password"]
        self.fields["password1"].help_text = text["password_help"]
        self.fields["password2"].label = text["password_confirm"]
        self.fields["password2"].help_text = text["password_confirm_help"]

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
    def __init__(self, *args, language="pt", **kwargs):
        super().__init__(*args, **kwargs)
        text = get_form_text(language)
        self.fields["month"].label = text["month"]
        self.fields["year"].label = text["year"]
        self.fields["income"].label = text["income"]

    class Meta:
        model = MonthlyBudget
        fields = ("month", "year", "income")
        widgets = {
            "month": forms.NumberInput(attrs={"min": 1, "max": 12}),
            "year": forms.NumberInput(attrs={"min": 2020, "max": 2100}),
        }


class FixedExpenseForm(forms.ModelForm):
    def __init__(self, *args, language="pt", **kwargs):
        super().__init__(*args, **kwargs)
        text = get_form_text(language)
        self.fields["name"].label = text["name"]
        self.fields["amount"].label = text["amount"]

    class Meta:
        model = FixedExpense
        fields = ("name", "amount")


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, language="pt", **kwargs):
        super().__init__(*args, **kwargs)
        text = get_form_text(language)
        self.fields["kind"].label = text["kind"]
        self.fields["kind"].choices = list(get_kind_labels(language).items())
        self.fields["date"].label = text["date"]
        self.fields["description"].label = text["description"]
        self.fields["category"].label = text["category"]
        self.fields["category"].choices = list(get_category_labels(language).items())
        self.fields["notes"].label = text["notes"]
        self.fields["notes"].widget.attrs["placeholder"] = text["optional"]
        self.fields["amount"].label = text["amount"]

    class Meta:
        model = Transaction
        fields = ("kind", "date", "description", "category", "notes", "amount")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(),
        }


class LocalizedAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, language="pt", **kwargs):
        super().__init__(request, *args, **kwargs)
        text = get_form_text(language)
        self.fields["username"].label = text["username"]
        self.fields["password"].label = text["password"]
