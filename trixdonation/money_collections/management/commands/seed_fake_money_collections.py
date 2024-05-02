import os
import random
import string
from faker import Faker
from django.core.management.base import BaseCommand
from money_collections.models import MoneyCollection, MoneyCollectionRequisites, Report, ReportImage, ReportVideo, Subscription
from organizations.models import Organization
from users.models import User
from money_collections.models.bank_card import BankCard
from money_collections.models.other_requisite import OtherRequisite

fake = Faker()

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_credit_card():
    first_digit = random.randint(1, 9)  # Випадкове число від 1 до 9
    rest_digits = ''.join(random.choices('0123456789', k=15))  # Рандомні 15 цифр
    return str(first_digit) + rest_digits

def generate_fake_subscriptions(money_collection):
    users = User.objects.all()
    for _ in range(fake.random_int(min=0, max=3)):
        user = fake.random_element(users)
        subscription = Subscription(user=user, money_collection=money_collection)
        subscription.save()


class Command(BaseCommand):
    help = 'Seed the database with fake data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding the database with fake data...")

        preview_directory = 'organizations/management/avatars'
        report_image_directory = 'organizations/management/images'
        report_video_directory = 'organizations/management/videos'
        preview_files = os.listdir(preview_directory)
        preview_usage_count = {image_filename: 0 for image_filename in preview_files}
        report_image_files = os.listdir(report_image_directory)
        report_image_usage_count = {image_filename: 0 for image_filename in report_image_files}
        report_video_files = os.listdir(report_video_directory)
        report_video_usage_count = {video_filename: 0 for video_filename in report_video_files}

        for _ in range(30):
            organization = Organization.objects.order_by('?').first()
            preview_filename = min(preview_usage_count, key=preview_usage_count.get)
            preview_usage_count[preview_filename] += 1
            collection_data = {
                'goal_title': fake.sentence(),
                'description': fake.paragraph(),
                'active': fake.boolean(),
                'collected_amount_on_jar': fake.pydecimal(left_digits=4, right_digits=2),
                'collected_amount_on_platform': fake.pydecimal(left_digits=4, right_digits=2),
                'collected_amount_from_other_requisites': fake.pydecimal(left_digits=4, right_digits=2),
                "goal_amount": fake.pydecimal(left_digits=8, right_digits=2),
            }
            collection = MoneyCollection(**collection_data)
            preview_path = os.path.join(preview_directory, preview_filename)
            collection.preview.save(preview_filename, open(preview_path, 'rb'), save=True)
            collection.save()

            generate_fake_subscriptions(collection) 

            organization.money_collections.add(collection)  
            organization.save()

            requisites_data = {
                'money_collection': collection,
                'monobank_jar_link': "https://send.monobank.ua/jar/8KJGWhCcvm",
                'monobank_jar_number': "5375411216494380",
                'paypal_email': fake.email(),
                'bitcoin_wallet_address': generate_random_string(42),
                'ethereum_wallet_address': generate_random_string(42),
                'usdt_wallet_address': generate_random_string(34),
            }
            requisites = MoneyCollectionRequisites.objects.create(**requisites_data)

            # Create bank cards
            bank_cards = []
            for _ in range(fake.random_int(min=0, max=3)):
                bank_card_data = {
                    'bank_name': fake.company(),
                    'card_number': generate_random_credit_card(),
                }
                bank_card = BankCard.objects.create(**bank_card_data)
                bank_cards.append(bank_card)
        
            # Associate bank cards with MoneyCollectionRequisites
            requisites.bank_cards.set(bank_cards)
        
            # Create other requisites
            other_requisites = []
            for _ in range(fake.random_int(min=0, max=3)):
                other_requisite_data = {
                    'name': fake.word(),
                    'value': fake.word(),
                }
                other_requisite = OtherRequisite.objects.create(**other_requisite_data)
                other_requisites.append(other_requisite)
        
            # Associate other requisites with MoneyCollectionRequisites
            requisites.other_requisites.set(other_requisites)

            for _ in range(fake.random_int(min=0, max=3)):
                report_data = {
                    'money_collection': collection,
                    'name': fake.sentence(),
                    'price': fake.pydecimal(left_digits=3, right_digits=2),
                    'description': fake.paragraph(),
                }
                report = Report.objects.create(**report_data)

                for _ in range(fake.random_int(min=0, max=3)):
                    image_filename = min(report_image_usage_count, key=report_image_usage_count.get)
                    report_image_usage_count[image_filename] += 1
                    image_path = os.path.join(report_image_directory, image_filename)
                    report_image = ReportImage()
                    with open(image_path, 'rb') as image_file:
                        report_image.file.save(image_filename, image_file, save=True)
                    report.images.add(report_image)

                for _ in range(fake.random_int(min=0, max=2)):
                    video_filename = min(report_video_usage_count, key=report_video_usage_count.get)
                    report_video_usage_count[video_filename] += 1
                    video_path = os.path.join(report_video_directory, video_filename)
                    report_video = ReportVideo()
                    with open(video_path, 'rb') as video_file:
                        report_video.file.save(video_filename, video_file, save=True)
                    report.videos.add(report_video)

        self.stdout.write(self.style.SUCCESS("Fake data seeding completed successfully!"))
