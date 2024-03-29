# Generated by Django 4.0.4 on 2022-05-24 11:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("explore", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="area",
            name="name",
            field=models.SlugField(help_text="The name of the area."),
        ),
        migrations.AlterField(
            model_name="origin",
            name="url",
            field=models.URLField(blank=True, help_text="A link to origin details."),
        ),
    ]
