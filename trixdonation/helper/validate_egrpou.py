import requests
import xml.etree.ElementTree as ET

from organizations.models.oranizations import OrganizationRequest

def validate_egrpou(egrpou_code):
    url = f"https://adm.tools/action/gov/api/?egrpou={egrpou_code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    root = ET.fromstring(response.text)
    if root:
        name_short = root.find(".//company").get("name_short")
        if not name_short.startswith("БО"):
            return False, "Заданий ЄДРПОУ не відповідає ЄДРПОУ благодійної організації."
        if OrganizationRequest.objects.filter(EGRPOU_code=egrpou_code, status='a').exists():
            return False, "Фонд з таким ЄДРПОУ вже зареєстрований. Якщо ви вважаєте, що це зловмисник, будь ласка зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com."
        return True, ""
    else:
        return False, "Заданий ЄДРПОУ не існує, якщо ви вважаєте, що сталася помилка, будь ласка зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com."
