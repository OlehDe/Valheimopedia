from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.db import transaction

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Спроба знайти існуючого користувача за email
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                # Якщо знайшли, прив'язуємо соціальний акаунт до існуючого користувача
                sociallogin.connect(request, user)
            except User.MultipleObjectsReturned:
                # Якщо знайшли декілька, беремо першого
                user = User.objects.filter(email=email).first()
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass