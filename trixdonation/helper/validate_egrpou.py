import requests
import xml.etree.ElementTree as ET

from organizations.models.oranizations import OrganizationRequest

def validate_egrpou(egrpou_code):
    response = requests.get(f"https://adm.tools/action/gov/api/?egrpou={egrpou_code}")
    root = ET.fromstring(response.content)
    if root:
        name_short = root.find(".//company").get("name_short")
        if not name_short.startswith("БО"):
            return False, "Заданий ЄДРПОУ не відповідає ЄДРПОУ благодійної організації."
        if OrganizationRequest.objects.filter(EGRPOU_code=egrpou_code, status='a').exists():
            return False, "Фонд з таким ЄДРПОУ вже зареєстрований. Якщо ви вважаєте, що це зловмисник, будь ласка зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com."
        return True, ""
    else:
        return False, "Заданий ЄДРПОУ не існує, якщо ви вважаєте, що сталася помилка, будь ласка зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com."
