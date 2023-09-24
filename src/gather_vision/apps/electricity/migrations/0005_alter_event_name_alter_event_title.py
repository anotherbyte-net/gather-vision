# Generated by Django 5.0a1 on 2023-09-24 13:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("electricity", "0004_event_gatherer_usage_gatherer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="name",
            field=models.SlugField(
                help_text="The internal name of the record.", max_length=300
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="title",
            field=models.CharField(help_text="The displayed title.", max_length=300),
        ),
    ]
