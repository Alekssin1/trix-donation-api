import os
from celery import shared_task
from .services import handle_user
import logging

from django.utils import timezone

from users.models import User

logger = logging.getLogger("Email")
logger2 = logging.getLogger("remove_old_not_activated_users")


@shared_task
def send_password_recovery_email(email, name, surname, code):
    logger.info("Log have  no sence *******************")
    handle_user.handle_send_password_recovery(email, name, surname, code)

@shared_task
def send_email_verification_email(email, code):
    handle_user.handle_send_email_verify(email, code)

@shared_task
def remove_old_image(old_avatar_path):
    if old_avatar_path and not old_avatar_path.endswith('.webp'):
        try:
            os.remove(old_avatar_path)
        except FileNotFoundError:
            pass


@shared_task
def remove_old_not_activated_users():
    """ tasks runs every day at 11:30 pm """

    logger2.info("remove_old_not_activated_users start")
    
    delete_after_date = timezone.now() - timezone.timedelta(days=User.REMOVE_UNACTIVE_USER_DAYS_AFTER)
    
    unactive_users = User.objects.filter(is_active=False, registration_date__lte=delete_after_date)

    logger.info(f"declined_requests count = {unactive_users.count()}")

    unactive_users.delete()

    logger.info("remove_old_not_activated_users end")


