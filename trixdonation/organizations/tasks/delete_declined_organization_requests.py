
from celery import shared_task
import logging
from django.utils import timezone

from organizations.models import OrganizationRequest

logger = logging.getLogger('delete_declined_organization_requests')


@shared_task
def delete_declined_organization_requests():

    """ tasks runs every day at 11:30 pm """

    logger.info("delete_declined_organization_requests start")
    
    delete_after_date = timezone.now() - timezone.timedelta(days=OrganizationRequest.REMOVE_DECLINED_REQUESTS_AFTER_DAYS)
    
    declined_requests = OrganizationRequest.objects.filter(status=OrganizationRequest.DECLINED, status_changed_at__lte=delete_after_date)

    logger.info(f"declined_requests count = {declined_requests.count()}")

    declined_requests.delete()

    logger.info("delete_declined_organization_requests end")




