# Generated by Django 2.2 on 2020-04-09 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regulations', '0009_attendancedateperson'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attendancedateperson',
            old_name='early_attendances',
            new_name='early_leaves',
        ),
    ]