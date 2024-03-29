# Generated by Django 5.0a1 on 2023-09-24 13:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("explore", "0004_gatherer_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="area",
            name="name",
            field=models.SlugField(
                help_text="The internal name of the record.", max_length=300
            ),
        ),
        migrations.AlterField(
            model_name="area",
            name="title",
            field=models.CharField(help_text="The displayed title.", max_length=300),
        ),
        migrations.AlterField(
            model_name="gatherer",
            name="name",
            field=models.SlugField(
                help_text="The internal name of the record.", max_length=300
            ),
        ),
        migrations.AlterField(
            model_name="gatherer",
            name="title",
            field=models.CharField(help_text="The displayed title.", max_length=300),
        ),
        migrations.AlterField(
            model_name="origin",
            name="name",
            field=models.SlugField(
                help_text="The internal name of the record.", max_length=300
            ),
        ),
        migrations.AlterField(
            model_name="origin",
            name="title",
            field=models.CharField(help_text="The displayed title.", max_length=300),
        ),
    ]
