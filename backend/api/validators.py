from rest_framework import exceptions

BANNED_USERNAMES = (
    'me', 'set_password',
)


def validate_username(value):
    value = value.lower()
    if value in BANNED_USERNAMES:
        raise exceptions.ValidationError('Некорректное имя пользователя.')
    return value
