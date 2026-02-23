from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from .services.email_service import send_activation_email


@receiver(post_save, sender=User)
def send_activation_email_signal(sender, instance, created, **kwargs):
    if created:

        def send_email():
            uidb64 = urlsafe_base64_encode(force_bytes(instance.pk))
            token = default_token_generator.make_token(instance)
            send_activation_email(instance, token, uidb64)

        transaction.on_commit(send_email)