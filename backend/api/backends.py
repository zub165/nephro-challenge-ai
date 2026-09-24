from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Allow login with username or email (case-insensitive email)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        login = username.strip()
        user = None

        if "@" in login:
            try:
                user = User.objects.get(email__iexact=login)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=login)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
