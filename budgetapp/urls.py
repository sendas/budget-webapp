from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from finance import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("preferencias/", views.preferences_update, name="preferences_update"),
    path("registo/", views.signup, name="signup"),
    path("pendente/", views.pending_approval, name="pending_approval"),
    path("", views.dashboard, name="dashboard"),
    path("orcamento/novo/", views.budget_create, name="budget_create"),
    path("orcamento/<int:budget_id>/", views.budget_detail, name="budget_detail"),
    path("orcamento/<int:budget_id>/fixas/nova/", views.fixed_expense_create, name="fixed_expense_create"),
    path("orcamento/<int:budget_id>/movimento/novo/", views.transaction_create, name="transaction_create"),
    path("fixas/<int:expense_id>/apagar/", views.fixed_expense_delete, name="fixed_expense_delete"),
    path("movimentos/<int:transaction_id>/apagar/", views.transaction_delete, name="transaction_delete"),
]
