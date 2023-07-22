# flake8: noqa
import json

from django.core.management.base import BaseCommand

from foodgram_backend.settings import (
    FILE_PATH,
    FILE_PATH_TAGS,
    FILE_PATH_USERS
)
from recipes.models import Ingredient, Tag
from users.models import User


class Command(BaseCommand):
    help = 'Загрузка данных из JSON файла в таблицу Ingredients'

    def handle(self, *args, **options):
        with open(FILE_PATH, encoding="utf8") as f:
            data = json.load(f)
            for item in data:
                try:
                    Ingredient.objects.create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit']
                    )
                except:
                    pass
        with open(FILE_PATH_TAGS, encoding="utf8") as f:
            data = json.load(f)
            for item in data:
                try:
                    Tag.objects.create(
                        name=item['name'],
                        color=item['color'],
                        slug=item['slug']
                    )
                except:
                    pass
        with open(FILE_PATH_USERS, encoding="utf8") as f:
            data = json.load(f)
            for item in data:
                try:
                    user = User.objects.create(
                        username=item['username'],
                        first_name=item['first_name'],
                        last_name=item['last_name'],
                        email=item['email'],
                        password=item['password']
                    )
                    user.set_password(item['password'])
                    user.save()
                except:
                    pass
        self.stdout.write(
            self.style.SUCCESS('Загрузка данных прошла успешно.'))
