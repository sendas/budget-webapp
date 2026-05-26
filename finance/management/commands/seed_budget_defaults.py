from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Mostra as categorias iniciais espelhadas do ficheiro Excel original."

    def handle(self, *args, **options):
        self.stdout.write("Despesas fixas sugeridas: renda/casa, agua, eletricidade, internet, transporte, credito, telefone.")
        self.stdout.write("Categorias diarias e BONGO ja estao disponiveis nos formularios.")
