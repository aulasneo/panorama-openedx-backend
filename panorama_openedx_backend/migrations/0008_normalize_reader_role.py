"""Correct the historical default without modifying explicit author grants."""

from django.db import migrations, models


def normalize_reader(apps, schema_editor):
    """Repair only the known historical spelling on the migration's database."""
    access = apps.get_model('panorama_openedx_backend', 'UserAccessConfiguration')
    access.objects.using(schema_editor.connection.alias).filter(role='Reader').update(role='READER')


class Migration(migrations.Migration):
    dependencies = [('panorama_openedx_backend', '0007_remove_ai_author_role')]

    operations = [
        # Reversal cannot identify which uppercase readers were originally mixed case.
        migrations.RunPython(normalize_reader, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='useraccessconfiguration', name='role',
            field=models.CharField(choices=[('READER', 'Reader'), ('AUTHOR', 'Author')],
                                   default='READER', help_text='User role', max_length=20),
        ),
        migrations.AlterField(
            model_name='dashboardtype', name='student_view',
            field=models.BooleanField(default=False, verbose_name='Available to students', help_text=(
                "If enabled, these dashboards will be made available to students. "
                "Parameters 'userId' and 'lms' are client-controlled display filters, not access controls. "
                "Require dataset-side isolation for each learner and tenant before enabling student access."
            )),
        ),
    ]
