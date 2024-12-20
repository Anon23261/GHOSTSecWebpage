# Generated by Django 4.2.7 on 2024-11-15 00:04

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                (
                    "bio",
                    models.TextField(
                        blank=True, max_length=500, verbose_name="Biography"
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="avatars/%Y/%m/",
                        verbose_name="Avatar",
                    ),
                ),
                (
                    "skill_level",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Skill Level",
                    ),
                ),
                (
                    "experience_points",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Experience Points",
                    ),
                ),
                (
                    "two_factor_enabled",
                    models.BooleanField(
                        default=False, verbose_name="Two Factor Authentication Enabled"
                    ),
                ),
                (
                    "last_security_check",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Last Security Check"
                    ),
                ),
                (
                    "security_questions_set",
                    models.BooleanField(
                        default=False, verbose_name="Security Questions Set"
                    ),
                ),
                (
                    "last_password_change",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Last Password Change",
                    ),
                ),
                (
                    "failed_login_attempts",
                    models.IntegerField(
                        default=0, verbose_name="Failed Login Attempts"
                    ),
                ),
                (
                    "account_locked_until",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Account Locked Until"
                    ),
                ),
                (
                    "challenges_completed",
                    models.IntegerField(default=0, verbose_name="Challenges Completed"),
                ),
                (
                    "contributions",
                    models.IntegerField(
                        default=0, verbose_name="Community Contributions"
                    ),
                ),
                (
                    "reputation_points",
                    models.IntegerField(default=0, verbose_name="Reputation Points"),
                ),
                (
                    "badges",
                    models.JSONField(
                        blank=True, default=list, verbose_name="Earned Badges"
                    ),
                ),
                (
                    "last_active",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Last Active"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "indexes": [
                    models.Index(
                        fields=["username"], name="users_user_usernam_65d164_idx"
                    ),
                    models.Index(fields=["email"], name="users_user_email_6f2530_idx"),
                    models.Index(
                        fields=["skill_level"], name="users_user_skill_l_97a1d8_idx"
                    ),
                ],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
