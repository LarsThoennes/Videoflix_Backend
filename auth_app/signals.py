import os
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
    """
    Signal handler for sending activation emails.

    This signal handles:
    - detecting when a new User instance is created
    - generating a secure activation token
    - encoding the user ID for safe use in URLs
    - sending the activation email after the database transaction is committed
    """
    if created and os.environ.get("DISABLE_EMAIL") != "True":

        def send_email():
            uidb64 = urlsafe_base64_encode(force_bytes(instance.pk))
            token = default_token_generator.make_token(instance)
            send_activation_email(instance, token, uidb64)

        transaction.on_commit(send_email)