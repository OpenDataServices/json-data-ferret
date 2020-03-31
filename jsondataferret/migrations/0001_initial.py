# Generated by Django 3.0.6 on 2020-05-21 15:45

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Type",
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
                ("public_id", models.CharField(max_length=200, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Record",
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
                ("public_id", models.CharField(max_length=200)),
                ("cached_exists", models.BooleanField(default=False)),
                (
                    "cached_data",
                    django.contrib.postgres.fields.jsonb.JSONField(default=dict),
                ),
                (
                    "cached_jsonschema_validation_errors",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, null=True
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="jsondataferret.Type",
                    ),
                ),
            ],
            options={"unique_together": {("type", "public_id")},},
        ),
        migrations.CreateModel(
            name="Event",
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
                ("public_id", models.CharField(max_length=200, unique=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("comment", models.TextField(default="")),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Edit",
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
                ("public_id", models.CharField(max_length=200, unique=True)),
                ("mode", models.CharField(default="REPLACE", max_length=200)),
                ("data_key", models.TextField(default="/")),
                ("data", django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                (
                    "approval_event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="edits_approved",
                        to="jsondataferret.Event",
                    ),
                ),
                (
                    "creation_event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="edits_created",
                        to="jsondataferret.Event",
                    ),
                ),
                (
                    "record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="jsondataferret.Record",
                    ),
                ),
                (
                    "refusal_event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="edits_refused",
                        to="jsondataferret.Event",
                    ),
                ),
            ],
        ),
    ]
