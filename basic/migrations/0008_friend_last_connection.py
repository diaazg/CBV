# Generated by Django 5.1 on 2024-09-17 09:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("basic", "0007_remove_message_content_message_audio_file_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="friend",
            name="last_connection",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
