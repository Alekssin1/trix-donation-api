import os
from faker import Faker
from django.core.management.base import BaseCommand
from organizations.models import Organization, Post, PostImage, PostVideo, OrganizationSubscription
from users.models import User

fake = Faker()

def generate_fake_subscriptions(organization):
    users = User.objects.all()
    for _ in range(fake.random_int(min=0, max=3)):
        user = fake.random_element(users)
        if not OrganizationSubscription.objects.filter(user=user, organization=organization).exists():
            subscription = OrganizationSubscription(user=user, organization=organization)
            try:
                subscription.save()
            except:
                pass

class Command(BaseCommand):
    help = 'Seed the database with fake organizations and posts'
    

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding the database with fake organizations and posts...")

        avatar_directory = 'organizations/management/avatars'
        image_directory = 'organizations/management/images'
        video_directory = 'organizations/management/videos'
        avatar_files = os.listdir(avatar_directory)
        avatar_usage_count = {image_filename: 0 for image_filename in avatar_files}
        image_files = os.listdir(image_directory)
        image_usage_count = {image_filename: 0 for image_filename in image_files}
        video_files = os.listdir(video_directory)
        video_usage_count = {video_filename: 0 for video_filename in video_files}
        


        

        fake_users = User.objects.all()
        # Create fake organizations
        for _ in range(15):
            foundation = fake.boolean()
            if foundation:
                staff_users = fake_users.filter(organizations__isnull=True)[:fake.random_int(min=1, max=3)] 
                name = fake.company()
            else:
                staff_users = fake_users.filter(organizations__isnull=True)[:1]  
                name = f"{staff_users[0].name} {staff_users[0].surname}"
            avatar_filename = min(avatar_usage_count, key=avatar_usage_count.get)
            avatar_usage_count[avatar_filename] += 1
            organization_data = {
                'name': name,
                'twitter': 'https://x.com/serhiyprytula' if fake.boolean() else None,
                'instagram': 'https://www.instagram.com/amil_kurganagregat/' if fake.boolean() else None,
                'facebook': 'https://www.facebook.com/serhiyprytula/' if fake.boolean() else None,
                'customURL': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' if fake.boolean() else None,
                'foundation': foundation,
            }
            organization = Organization(**organization_data)
            avatar_path = os.path.join(avatar_directory, avatar_filename)
            organization.avatar.save(avatar_filename, open(avatar_path, 'rb'), save=True)
            organization.save()
            organization.created_by = staff_users[0]
            for user in staff_users:
                organization.staff.add(user) 
            

            generate_fake_subscriptions(organization) 


           # Create fake posts for the organization
            for _ in range(fake.random_int(min=1, max=5)):
                post_data = {
                    'organization': organization,
                    'name': fake.sentence(),
                    'description': fake.paragraph() if fake.boolean() else None,
                }
                post = Post.objects.create(**post_data)

                 # Attach fake images to the post
                for _ in range(fake.random_int(min=0, max=3)):
                    image_filename = min(image_usage_count, key=image_usage_count.get)
                    image_usage_count[image_filename] += 1
                    image_path = os.path.join(image_directory, image_filename)
                    post_image = PostImage()
                    with open(image_path, 'rb') as image_file:
                        post_image.file.save(image_filename, image_file, save=True)
                    post.images.add(post_image)

                # Attach fake videos to the post
                for _ in range(fake.random_int(min=0, max=2)):
                    video_filename = min(video_usage_count, key=video_usage_count.get)
                    video_usage_count[video_filename] += 1
                    video_path = os.path.join(video_directory, video_filename)
                    post_video = PostVideo()
                    with open(video_path, 'rb') as video_file:
                        post_video.file.save(video_filename, video_file, save=True)
                    post.videos.add(post_video)
                    
        self.stdout.write(self.style.SUCCESS("Fake organizations and posts seeding completed successfully!"))

