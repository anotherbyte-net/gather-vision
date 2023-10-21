# Generated by Django 5.0a1 on 2023-09-23 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("explore", "0004_gatherer_and_more"),
        ("transport", "0002_event_occurred_date_alter_event_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="gatherer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transport_events",
                to="explore.gatherer",
            ),
        ),
    ]