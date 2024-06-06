"""
Database models for panorama_openedx_backend.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel

User = get_user_model()

ROLES = [
    ("READER", "Reader"),
    ("AUTHOR", "Author"),
    ("AI_AUTHOR", "AI Author"),
]


class Dashboard(TimeStampedModel):
    """
    .. no_pii:.
    """

    dashboard_id = models.CharField(
        max_length=50,
        blank=False,
        primary_key=True,
        default='',
        unique=True,
        help_text=_("Quicksight Dashboard ID"),
    )

    name = models.CharField(
        max_length=50,
        blank=False,
        primary_key=False,
        default='',
        unique=True,
        help_text=_("Dashboard name"),
    )

    display_name = models.CharField(
        max_length=50,
        blank=False,
        primary_key=False,
        default='',
        unique=True,
        help_text=_("Dashboard display_name"),
    )

    priority = models.IntegerField(
        default=10,
        blank=False,
        help_text=_("Order of appearance in the menu. The lower the number, the higher the position.")
    )

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return self.name


class DashboardType(TimeStampedModel):
    """
    .. no_pii:.
    """

    name = models.CharField(
        max_length=50,
        blank=False,
        primary_key=True,
        default='',
        unique=True,
        help_text=_("Dashboard type name"),
    )

    dashboards = models.ManyToManyField("Dashboard")

    student_view = models.BooleanField(
        verbose_name="Available to students",
        default=False,
        help_text=_("If enabled, these dashboards will be made available to students. "
                    "Important: these dashboards must include the parameters 'userId' and 'lms', have filters "
                    "applying these parameters to all visuals, and the dashboard must be shared disabling users "
                    "to access any filter.")
    )

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return self.name


class UserAccessConfiguration(TimeStampedModel):
    """
    .. no_pii:.
    """

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    dashboard_type = models.ForeignKey(
        to="DashboardType",
        on_delete=models.CASCADE
    )

    arn = models.CharField(
        verbose_name='ARN',
        max_length=255,
        blank=False,
        primary_key=False,
        default='',
        unique=False,
        help_text=_("Quicksight user ARN"),
    )

    role = models.CharField(
        max_length=20,
        blank=False,
        primary_key=False,
        default='Reader',
        unique=False,
        choices=ROLES,
        help_text=_("User role"),
    )

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f'User {self.user}: {self.role} of {self.dashboard_type} dashboards as ARN {self.arn}'
