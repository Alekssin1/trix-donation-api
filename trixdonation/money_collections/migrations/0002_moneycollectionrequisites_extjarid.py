# Generated by Django 5.0.4 on 2024-05-10 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('money_collections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='moneycollectionrequisites',
            name='extJarId',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
