# Generated by Django 4.0.4 on 2022-05-15 14:19

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Area",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The date this record was created."
                    ),
                ),
                (
                    "modified_date",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The date this record was most recently modified.",
                    ),
                ),
                ("name", models.SlugField(help_text="The name of the event.")),
                (
                    "title",
                    models.CharField(help_text="The displayed title.", max_length=200),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("L1", "Country (level 1)"),
                            ("L2", "Region (level 2)"),
                            ("L3", "District (level 3)"),
                            ("L4", "Locality (level 4)"),
                            ("L5", "Neighbourhood (level 5)"),
                        ],
                        help_text="The division level.",
                        max_length=2,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Coordinate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The date this record was created."
                    ),
                ),
                (
                    "modified_date",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The date this record was most recently modified.",
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        decimal_places=5,
                        help_text="The latitude (North/South position, -90 to +90).",
                        max_digits=7,
                        validators=[
                            django.core.validators.MinValueValidator(-90),
                            django.core.validators.MaxValueValidator(90),
                        ],
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        decimal_places=5,
                        help_text="The longitude (East/West position -180 to +180).",
                        max_digits=8,
                        validators=[
                            django.core.validators.MinValueValidator(-180),
                            django.core.validators.MaxValueValidator(180),
                        ],
                    ),
                ),
                (
                    "reference_system",
                    models.SlugField(
                        blank=True,
                        help_text="The geographic spatial reference system for the coordinates.",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Origin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The date this record was created."
                    ),
                ),
                (
                    "modified_date",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The date this record was most recently modified.",
                    ),
                ),
                ("name", models.SlugField(help_text="The name of the origin.")),
                (
                    "title",
                    models.CharField(help_text="The displayed title.", max_length=200),
                ),
                (
                    "description",
                    models.TextField(help_text="The description of the origin."),
                ),
                (
                    "url",
                    models.URLField(blank=True, help_text="A link to event details."),
                ),
                (
                    "area",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="origins",
                        to="explore.area",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="coordinate",
            constraint=models.UniqueConstraint(
                fields=("latitude", "longitude", "reference_system"),
                name="explore_coordinate_unique_latitude_longitude_ref",
            ),
        ),
        migrations.AddField(
            model_name="area",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="The parent area that contains this area.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="explore.area",
            ),
        ),
        migrations.AddField(
            model_name="customuser",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="customuser",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddConstraint(
            model_name="origin",
            constraint=models.UniqueConstraint(
                fields=("name",), name="explore_area_unique_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="area",
            constraint=models.UniqueConstraint(
                fields=("name", "level", "parent"),
                name="explore_area_unique_name_level_parent",
            ),
        ),
    ]
