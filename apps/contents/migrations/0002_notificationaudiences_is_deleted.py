# Generated by Django 2.2 on 2020-02-11 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationaudiences',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
