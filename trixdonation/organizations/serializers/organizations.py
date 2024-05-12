from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from organizations.models import OrganizationRequest, Organization, OrganizationStaff
from helper.social_media_validation import is_valid_social_media_url


class OrganizationRequestGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRequest
        fields = '__all__'

    

class OrganizationRequestBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRequest
        exclude = ('created_at', 'status_changed_at', 'status', 'user')


    def validate(self, attrs):
        user = self.context.get('user')


        errors = []

        # Check if the user blocked to create organization or not
        if user.blocked:
            errors.append("Ви не можете надіслати запит, тому що ваш обліковий запис заблоковано для створення волонтерських сторінок або коштів. Якщо ви не згодні з цим рішенням, зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com.")
        
        # Check if user send EGRPOU when tried register foundation
        if attrs.get('foundation') == True and not attrs.get('EGRPOU_code'):
             errors.append("Для запиту на створення фонду необхідно ввести ЄДРПОУ код.")
        
        # Check urls user sends are valid
        if attrs.get('instagram_url') and not is_valid_social_media_url(attrs.get('instagram_url'), "instagram"):
            errors.append("Вказане вами посилання на instagram не є дійсним, будь ласка перевірте чи правильно ви задали посилання.")
        if attrs.get('twitter_url') and not is_valid_social_media_url(attrs.get('twitter_url'), "twitter"):
            errors.append("Вказане вами посилання на twitter(X) не є дійсним, будь ласка перевірте чи правильно ви задали посилання.")
        if attrs.get('facebook_url') and not is_valid_social_media_url(attrs.get('facebook_url'), "facebook"):
            errors.append("Вказане вами посилання на facebook не є дійсним, будь ласка перевірте чи правильно ви задали посилання.")

        if errors:
            raise ValidationError(errors)

        return attrs
    

class StaffOrganizationRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRequest
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.status_changed_at = timezone.now()
        instance.save()
        return instance
    
class OrganizationSerializerIds(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['organization_id', 'name']

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__' 


class OrganizationRequestPostSerializer(OrganizationRequestBaseSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context.get('user')

        errors = []

        # Check if user already has a request to register something
        request_exists = OrganizationRequest.objects.filter(user=user, status__in=['p', 'd']).exists()
        request_type = "фонду" if attrs.get('foundation') else "волонтерської сторінки"
        if request_exists:
            errors.append(f"Запит на створення {request_type} уже створений. Будь ласка очікуйте розгляду вашого запиту. Лист з відповідним рішенням прийде на вашу електронну пошту")
        # Check that user send at least one url and urls he sends are valid
        urls = [attrs.get('instagram_url'), attrs.get('twitter_url'), attrs.get('facebook_url'), attrs.get('custom_url')]
        if all(url is None for url in urls):
            errors.append("Для того щоб прийняти вас, нам необхідне хоча б 1 посилання, на ресурс, де ви вели волонтерську діяльність до того.")
        if errors:
            raise ValidationError(errors)
        return attrs

class OrganizationRequestUpdateSerializer(OrganizationRequestBaseSerializer):
    class Meta:
        model = OrganizationRequest
        fields = ['name', 'user_details', 'instagram_url', 'twitter_url', 'facebook_url', 'custom_url', 'image', 'EGRPOU_code']
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        # foundation = attrs.get('foundation', False)
        # print(foundation)
        # if not foundation and 'EGRPOU_code' in attrs:
        #     raise serializers.ValidationError('Ви не можете редагувати ЄДРПОУ, адже ваша заявка на реєстрацію волонтерської організації, а не фонду')
        return attrs
    
class OrganizationEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'twitter', 'instagram', 'facebook', 'customURL', 'avatar']
    
    def validate(self, attrs):
        errors = []

        if attrs.get('instagram') and not is_valid_social_media_url(attrs.get('instagram'), "instagram"):
            errors.append("Вказане вами посилання на Instagram не є дійсним, будь ласка, перевірте правильність посилання.")

        if attrs.get('twitter') and not is_valid_social_media_url(attrs.get('twitter'), "twitter"):
            errors.append("Вказане вами посилання на Twitter не є дійсним, будь ласка, перевірте правильність посилання.")

        if attrs.get('facebook') and not is_valid_social_media_url(attrs.get('facebook'), "facebook"):
            errors.append("Вказане вами посилання на Facebook не є дійсним, будь ласка, перевірте правильність посилання.")

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
    

class OrganizationStaffSerializer(serializers.ModelSerializer):
    from users.serializers import UserGetSerializer

    user = UserGetSerializer()

    class Meta:
        model = OrganizationStaff
        fields = ["user", "status"]

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

        



