# Generated by Django 5.1 on 2024-09-03 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("basic", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="friendship",
            name="last_connection",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]