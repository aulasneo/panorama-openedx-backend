from django.db import migrations, models


def migrate_ai_author_to_author(apps, schema_editor):
    user_access_configuration = apps.get_model(
        'panorama_openedx_backend',
        'UserAccessConfiguration',
    )
    user_access_configuration.objects.filter(role='AI_AUTHOR').update(role='AUTHOR')


class Migration(migrations.Migration):

    dependencies = [
        ('panorama_openedx_backend', '0006_alter_useraccessconfiguration_arn'),
    ]

    operations = [
        migrations.RunPython(
            migrate_ai_author_to_author,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='useraccessconfiguration',
            name='role',
            field=models.CharField(
                choices=[('READER', 'Reader'), ('AUTHOR', 'Author')],
                default='Reader',
                help_text='User role',
                max_length=20,
            ),
        ),
    ]
