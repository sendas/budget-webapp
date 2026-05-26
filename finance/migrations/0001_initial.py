import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MonthlyBudget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("month", models.PositiveSmallIntegerField()),
                ("year", models.PositiveSmallIntegerField()),
                ("income", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budgets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-year", "-month"]},
        ),
        migrations.CreateModel(
            name="FixedExpense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("budget", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fixed_expenses", to="finance.monthlybudget")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("DAILY", "Despesa diaria"), ("BONGO", "BONGO / extra")], default="DAILY", max_length=12)),
                ("date", models.DateField()),
                ("description", models.CharField(max_length=180)),
                ("category", models.CharField(choices=[("coffee", "Cafe"), ("drinks", "Bebidas"), ("food", "Comida"), ("shopping", "Compras"), ("entertainment", "Entretenimento"), ("transport", "Transporte"), ("health", "Saude"), ("other", "Outro"), ("fun", "Diversao"), ("clothes", "Roupa"), ("travel", "Viagens"), ("gifts", "Presentes"), ("repairs", "Reparacoes"), ("tech", "Tecnologia"), ("dining", "Restaurantes")], default="other", max_length=40)),
                ("notes", models.CharField(blank=True, max_length=240)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("budget", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="finance.monthlybudget")),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="monthlybudget",
            constraint=models.UniqueConstraint(fields=("owner", "month", "year"), name="unique_budget_per_user_month"),
        ),
    ]
