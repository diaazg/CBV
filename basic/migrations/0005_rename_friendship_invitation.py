# Generated by Django 5.1 on 2024-09-04 00:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("basic", "0004_friendship_accepted"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Friendship",
            new_name="Invitation",
        ),
    ]