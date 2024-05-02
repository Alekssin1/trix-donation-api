from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from helper.image_converter import convert_image_to_webp


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

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)
    surname = models.CharField(max_length=255, null=True)

    is_active = models.BooleanField(default=True) 

    registration_date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False) 
    admin = models.BooleanField(default=False)  

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True) 

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):  
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    def save(self, *args, **kwargs):
        if self.avatar:
            self.avatar = convert_image_to_webp(self.avatar)
        super().save(*args, **kwargs)