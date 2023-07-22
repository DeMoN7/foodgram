from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField('Логин', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('Email', max_length=254, unique=True)
    password = models.CharField('Пароль', max_length=150)


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follow')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_subscription')
        ]

        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user} subscribed on {self.author}'
