from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import FixedExpense, MonthlyBudget, Transaction


class AccessControlTests(TestCase):
    def test_signup_creates_inactive_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "novo",
                "email": "novo@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("pending_approval"))
        self.assertFalse(User.objects.get(username="novo").is_active)

    def test_user_cannot_view_another_users_budget(self):
        owner = User.objects.create_user("owner", password="StrongPass123!")
        other = User.objects.create_user("other", password="StrongPass123!")
        budget = MonthlyBudget.objects.create(owner=owner, month=4, year=2026, income=1000)

        self.client.force_login(other)
        response = self.client.get(reverse("budget_detail", args=[budget.id]))

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_users_records(self):
        owner = User.objects.create_user("owner", password="StrongPass123!")
        other = User.objects.create_user("other", password="StrongPass123!")
        budget = MonthlyBudget.objects.create(owner=owner, month=4, year=2026, income=1000)
        fixed = FixedExpense.objects.create(budget=budget, name="Internet", amount=40)
        transaction = Transaction.objects.create(
            budget=budget,
            kind=Transaction.Kind.DAILY,
            date=date(2026, 4, 10),
            description="Cafe",
            category="coffee",
            amount=2,
        )

        self.client.force_login(other)
        fixed_response = self.client.post(reverse("fixed_expense_delete", args=[fixed.id]))
        transaction_response = self.client.post(reverse("transaction_delete", args=[transaction.id]))

        self.assertEqual(fixed_response.status_code, 404)
        self.assertEqual(transaction_response.status_code, 404)
        self.assertTrue(FixedExpense.objects.filter(id=fixed.id).exists())
        self.assertTrue(Transaction.objects.filter(id=transaction.id).exists())

    def test_preferences_update_language_and_theme(self):
        response = self.client.post(
            reverse("preferences_update"),
            {"language": "en", "theme": "dark", "next": reverse("login")},
        )

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(self.client.session["language"], "en")
        self.assertEqual(self.client.session["theme"], "dark")

        login_response = self.client.get(reverse("login"))
        self.assertContains(login_response, "Log in to financebros")
        self.assertContains(login_response, 'data-theme="dark"')
