# Generated by Django 5.1 on 2024-09-03 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("basic", "0003_room"),
    ]

    operations = [
        migrations.AddField(
            model_name="friendship",
            name="accepted",
            field=models.BooleanField(default=False),
        ),
    ]
