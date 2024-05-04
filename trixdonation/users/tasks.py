from celery import shared_task
from .services import handle_user
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
logger = logging.getLogger("Email")


@shared_task
def send_password_recovery_email(email, name, surname, code):
    logger.info("Log have  no sence *******************")
    handle_user.handle_send_password_recovery(email, name, surname, code)

@shared_task
def send_email_verification_email(email, code):
    handle_user.handle_send_email_verify(email, code)

# def handle_send_email_verify(email, code):
    # context = {
    #     "code": code,
    #     "page": "email_confirmation"
    # }

    # template = render_to_string(
    #     "email_code_send.html", context)

    # send_mail(
    #     "Підтвердження електронної адреси",
    #     "",
    #     "gamesdistributoragency@gmail.com",
    #     [email],
    #     fail_silently=False,
    #     html_message=template
    # )