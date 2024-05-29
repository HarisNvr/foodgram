import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    models_files = {
        Ingredient: 'ingredients.csv',
    }

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_PATH
        for model, filename in self.models_files.items():
            self.import_data(model, os.path.join(csv_path, filename))

    def import_data(self, model, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                ingredient_id = 1
                for row in reader:
                    if model == Ingredient:
                        model.objects.update_or_create(
                            id=ingredient_id,
                            defaults=row
                        )
                        ingredient_id += 1
            self.stdout.write(self.style.SUCCESS(f'Импортирован {filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка {filename}: {e}'))
