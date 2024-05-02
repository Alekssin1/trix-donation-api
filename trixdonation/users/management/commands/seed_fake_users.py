import os
import uuid 
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with fake users'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding the database with fake users...")

        avatar_directory = 'users/management/avatars'
        avatar_files = os.listdir(avatar_directory)
        avatar_usage_count = {image_filename: 0 for image_filename in avatar_files}

        for _ in range(40):
            avatar_filename = min(avatar_usage_count, key=avatar_usage_count.get)
            avatar_usage_count[avatar_filename] += 1
            
            user_data = {
                'email': fake.email(),
                'name': fake.first_name(),
                'surname': fake.last_name(),
                'password': make_password("doesn't matter"),
            }

            user = User(**user_data)
            avatar_path = os.path.join(avatar_directory, avatar_filename)
            user.avatar.save(avatar_filename, open(avatar_path, 'rb'), save=True)
            user.save()
            

        self.stdout.write(self.style.SUCCESS("Fake users seeding completed successfully!"))