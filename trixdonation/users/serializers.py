from rest_framework import serializers
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'surname', 'contact_number', 'avatar']


class EmailSerializer(serializers.Serializer):

    email = serializers.EmailField()


class PasswordCodeValidateSerializer(serializers.Serializer):

    email = serializers.EmailField()
    code = serializers.IntegerField()


