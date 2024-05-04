from django.contrib.auth import get_user_model
from users.models import User

from django.core.mail import send_mail
from django.template.loader import render_to_string


def get_user_by_email(email):
    return get_user_model().objects.get(email=email)

def is_email_verified(email):
    try:
        user = User.objects.get(email=email)
        return user.is_active
    except User.DoesNotExist:
        return True

def handle_send_password_recovery(email, name, surname, code):

    context = {
        "code": code,
        "name": name,
        "surname": surname,
        "page": 'password_reset'
    }

    template = render_to_string(
        "email_code_send.html", context)

    send_mail(
        "Відновлення паролю",
        "",
        "gamesdistributoragency@gmail.com",
        [email],
        fail_silently=False,
        html_message=template
    )



def handle_send_email_verify(email, code):

    context = {
        "code": code,
        "page": "email_confirmation"
    }

    template = render_to_string(
        "email_code_send.html", context)

    send_mail(
        "Підтвердження електронної адреси",
        "",
        "gamesdistributoragency@gmail.com",
        [email],
        fail_silently=False,
        html_message=template
    )