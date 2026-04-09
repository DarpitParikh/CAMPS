from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allocation', '0009_add_subject_elective_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='must_change_password',
            field=models.BooleanField(default=False),
        ),
    ]
