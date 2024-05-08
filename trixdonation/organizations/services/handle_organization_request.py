from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def handle_update_status_email_send(email, name, surname, status, foundation, organization_name):

    context = {
        "status": status,
        "name": name,
        "surname": surname,
        "foundation": foundation,
        "organization_name": organization_name,
    }

    template = render_to_string(
        "updated_status_email_send.html", context)

    organization = "фонду" if foundation else "волонтерської організації" 

    send_mail(
        f"Запит на створення {organization}",
        "",
        "gamesdistributoragency@gmail.com",
        [email],
        fail_silently=False,
        html_message=template
    )

def handle_foundation_invitation(email, pk, foundation_name, name, surname):
    base_url = settings.BASE_URLS.get(settings.ENVIRONMENT, 'http://127.0.0.1:8000')
    context = {
        "pk": pk,
        "name": name,
        "surname": surname,
        "foundation_name": foundation_name,
        "BASE_URL" : base_url
    }

    template = render_to_string(
        "fond_invitation_send.html", context)
    
   
    send_mail(
        f"Запрошення у {foundation_name}",
        "",
        "gamesdistributoragency@gmail.com",
        [email],
        fail_silently=False,
        html_message=template
    )
