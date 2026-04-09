from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('allocation', '0010_faculty_must_change_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='seat_no',
        ),
        migrations.RemoveField(
            model_name='resultsheet',
            name='seat_no',
        ),
    ]
