from celery import shared_task
from organizations.services import handle_organization_request


@shared_task
def send_found_invitation(email, pk, foundation_name, name, surname):
    handle_organization_request.handle_foundation_invitation(email, pk, foundation_name, name, surname)
