import os
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Invalid Email")
        if not password:
            raise ValueError("Invalid password")

        user = self.model(
            email=self.normalize_email(email), 
            **extra_fields

        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password, **extra_fields):
        """
        Creates and saves a staff user with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        user = self.create_user(
            email,
            password=password,
            **extra_fields
        )
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('admin', True)
        user = self.create_user(
            email,
            password=password, 
            **extra_fields
        )
        return user



class User(AbstractBaseUser):

    MAXIMUM_RECLINED_REQUESTS = 5
    REMOVE_UNACTIVE_USER_DAYS_AFTER = 5

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)
    surname = models.CharField(max_length=255, null=True)

    is_active = models.BooleanField(default=True) 

    registration_date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False) 
    admin = models.BooleanField(default=False)  

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True) 
    blocked = models.BooleanField(default=False, null=True, blank=True)
    declined_request_counter = models.IntegerField(default=0, null=True, blank=True)

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):  
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    def save(self, *args, **kwargs):

        from helper.image_converter import convert_image_to_webp


        if self.avatar and self.pk:  
            old_user = User.objects.get(pk=self.pk)
            if old_user.avatar:  
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(old_user.avatar))
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
                self.avatar.name = os.path.basename(old_user.avatar.name)
            self.avatar = convert_image_to_webp(self.avatar)
        super().save(*args, **kwargs)


        