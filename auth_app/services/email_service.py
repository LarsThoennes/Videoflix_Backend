from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logo_url = f"{settings.SITE_URL}/static/images/logo_icon.svg"
homepage_url = settings.SITE_URL

def send_activation_email(user, token, uidb64):
    """
    Send an account activation email to a newly registered user.

    This function handles:
    - generating the activation link containing the encoded user ID and token
    - rendering the HTML email template
    - providing a plain text fallback version
    - sending a multipart email (text + HTML) to the user's email address
    """
    activation_link = (f"{settings.SITE_URL}/activate-account/{uidb64}/{token}/")

    subject = "Confirm your email"

    # Text-Version (Fallback)
    text_content = (
        "Thank you for registering with Videoflix.\n\n"
        "To complete your registration and verify your email address,\n\n"
        "please click the link below:\n\n"
        f"{activation_link}"
    )

    # HTML-Version aus Template
    html_content = render_to_string(
        "emails/activation_email.html",
        {
            "user": user,
            "activation_link": activation_link,
            "logo_url": logo_url,
            "homepage_url": homepage_url,
        },
    )

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        None,
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_reset_password_email(user, token, uidb64):
    """
    Send a password reset email to a user.

    This function handles:
    - generating a secure password reset link with token and encoded user ID
    - rendering the HTML password reset email template
    - providing a plain text fallback version
    - sending a multipart email (text + HTML) to the user's email address
    """
    reset_link = (f"{settings.SITE_URL}reset-password/{uidb64}/{token}/")

    subject = "Reset your Password"

    # Text-Version (Fallback)
    text_content = (
        "We recently received a request to reset your password."
        "If you made this request, click the link below to reset your password:"
        f"{reset_link}"
    )

    # HTML-Version aus Template
    html_content = render_to_string(
        "emails/reset_password_email.html",
        {
            "user": user,
            "reset_link": reset_link,
            "logo_url": logo_url,
        },
    )

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        None,
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()