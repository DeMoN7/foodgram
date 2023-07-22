from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
# from django.urls import reverse


User = get_user_model()


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='someuser')
        cls.author = User.objects.create_user(username='author')

        cls.url_exists = {
            '/': HTTPStatus.OK,
            '/recipe/': HTTPStatus.OK,
            '/tags/': HTTPStatus.OK,
            '/posts/unexisting_page/': HTTPStatus.NOT_FOUND,
        }

    def setUp(self) -> None:
        # Создаем неавторизованный клиент.
        self.guest_client = Client()
        # Создаем второй клиент.
        self.autorized_client = Client()
        # Авторизуем пользователя 'someuser'.
        self.autorized_client.force_login(self.user)

    def test_url_exists_for_guest_client(self):
        """Страницы с общим доступом доступны любому пользователю."""
        """Несуществующая страница /unexisting_page/ не доступна."""
        self.url_exists['/create/'] = HTTPStatus.FOUND
        for page_name, status in self.url_exists.items():
            with self.subTest(page_name=page_name):
                self.assertEqual(
                    self.guest_client.get(page_name).status_code,
                    status
                )
