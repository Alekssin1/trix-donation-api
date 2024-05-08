from celery import shared_task
from organizations.services import handle_organization_request

from django.utils import timezone

from users.models import User

@shared_task
def send_updated_status_email(email, name, surname, status, foundation, organization_name):
    handle_organization_request.handle_update_status_email_send(email, name, surname, status, foundation, organization_name)
