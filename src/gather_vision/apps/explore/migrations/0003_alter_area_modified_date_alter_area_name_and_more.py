# Generated by Django 4.2.5 on 2023-09-10 08:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("explore", "0002_alter_area_name_alter_origin_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="area",
            name="modified_date",
            field=models.DateTimeField(
                auto_now=True,
                help_text="The date this record was most recently changed.",
            ),
        ),
        migrations.AlterField(
            model_name="area",
            name="name",
            field=models.SlugField(help_text="The internal name of the record."),
        ),
        migrations.AlterField(
            model_name="coordinate",
            name="modified_date",
            field=models.DateTimeField(
                auto_now=True,
                help_text="The date this record was most recently changed.",
            ),
        ),
        migrations.AlterField(
            model_name="origin",
            name="description",
            field=models.TextField(
                blank=True, help_text="The description of the record."
            ),
        ),
        migrations.AlterField(
            model_name="origin",
            name="modified_date",
            field=models.DateTimeField(
                auto_now=True,
                help_text="The date this record was most recently changed.",
            ),
        ),
        migrations.AlterField(
            model_name="origin",
            name="name",
            field=models.SlugField(help_text="The internal name of the record."),
        ),
        migrations.AlterField(
            model_name="origin",
            name="url",
            field=models.URLField(
                blank=True, help_text="A link to the record details."
            ),
        ),
    ]
