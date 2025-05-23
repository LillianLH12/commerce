# Generated by Django 5.2.1 on 2025-05-17 01:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0003_bid"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="is_closed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="listing",
            name="winner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="won_auctions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
