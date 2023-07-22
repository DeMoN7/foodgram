import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для картинки"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='rec.' + ext)
        return super().to_internal_value(data)


def get_ingredients_for_file(ingredients):
    """Получение списка ингредиентов для выгрузки"""
    ing_dct = {}
    for el in ingredients:
        if el.ingredients not in ing_dct:
            ing_dct[el.ingredients] = [
                el.ingredients.name,
                el.ingredients.measurement_unit,
                el.amount]
        ing_dct[el.ingredients][2] += el.amount
    return (ing_dct[el][0].title() + ' (' + ing_dct[el][1] + ') -- '
            + str(ing_dct[el][2]) + '\n' for el in ing_dct)
