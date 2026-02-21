from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_activation_email(user, token, uidb64):
    activation_link = (f"http://localhost:8000/api/activate/{uidb64}/{token}/")

    subject = "Willkommen bei Videoflix"

    # Text-Version (Fallback)
    text_content = (
        "Vielen Dank für Ihre Registrierung bei Videoflix!\n\n"
        "Bitte klicken Sie auf den folgenden Link, um Ihr Konto zu aktivieren:\n"
        f"{activation_link}"
    )

    # HTML-Version aus Template
    html_content = render_to_string(
        "emails/activation_email.html",
        {
            "user": user,
            "activation_link": activation_link,
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
