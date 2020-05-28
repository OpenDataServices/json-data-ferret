# Generated by Django 3.0.6 on 2020-05-28 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jsondataferret", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="JSONDataFerret",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("admin", "Can Admin All Data Managed by JSON Data Ferret"),
                ),
                "managed": False,
            },
        ),
    ]
