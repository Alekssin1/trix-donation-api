from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from django.template.loader import render_to_string


def get_user_by_email(email):
    return get_user_model().objects.get(email=email)


def handle_send_email_verify(email, code):

    context = {
        "code": code,
        "page": "email_confirmation"
    }

    template = render_to_string(
        "email_code_send.html", context)

    send_mail(
        "Verify email",
        "",
        "gamesdistributoragency@gmail.com",
        [email],
        fail_silently=False,
        html_message=template
    )