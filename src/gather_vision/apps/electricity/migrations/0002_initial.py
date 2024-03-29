# Generated by Django 4.0.4 on 2022-05-15 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("electricity", "0001_initial"),
        ("explore", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usage",
            name="origin",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="electricity_usages",
                to="explore.origin",
            ),
        ),
        migrations.AddField(
            model_name="progress",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="progression",
                to="electricity.event",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="area",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="electricity_event_areas",
                to="explore.area",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="origin",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="electricity_events",
                to="explore.origin",
            ),
        ),
        migrations.AddConstraint(
            model_name="usage",
            constraint=models.UniqueConstraint(
                fields=("occurred_date", "origin"),
                name="electricity_usage_unique_issued_date_origin",
            ),
        ),
        migrations.AddConstraint(
            model_name="progress",
            constraint=models.UniqueConstraint(
                fields=("occurred_date", "event"),
                name="electricity_progress_unique_occurred_date_event",
            ),
        ),
        migrations.AddConstraint(
            model_name="event",
            constraint=models.UniqueConstraint(
                fields=("name", "origin"), name="electricity_event_unique_name_origin"
            ),
        ),
    ]
