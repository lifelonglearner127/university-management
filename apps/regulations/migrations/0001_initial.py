# Generated by Django 2.2 on 2020-01-16 23:39

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AttendancePlace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=500)),
                ('longitude', models.DecimalField(decimal_places=10, max_digits=20)),
                ('latitude', models.DecimalField(decimal_places=10, max_digits=20)),
                ('radius', models.PositiveIntegerField(default=100)),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendanceRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('must_attendance_days', django.contrib.postgres.fields.ArrayField(base_field=models.DateField(), blank=True, null=True, size=None)),
                ('never_attendance_days', django.contrib.postgres.fields.ArrayField(base_field=models.DateField(), blank=True, null=True, size=None)),
                ('attendance_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='regulations.AttendancePlace')),
                ('attendees', models.ManyToManyField(related_name='attendee_rules', through='regulations.AttendanceMembership', to='teachers.TeacherProfile')),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('open_time', models.TimeField()),
                ('start_open_time', models.TimeField()),
                ('finish_open_time', models.TimeField()),
                ('close_time', models.TimeField()),
                ('start_close_time', models.TimeField()),
                ('finish_close_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='UnAttendenceMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_on', models.DateTimeField(auto_now_add=True)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regulations.AttendanceRule')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.TeacherProfile')),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('slots', models.ManyToManyField(to='regulations.TimeSlot')),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='fri',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fris', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='mon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mons', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='nonattendees',
            field=models.ManyToManyField(related_name='nonattendee_rules', through='regulations.UnAttendenceMembership', to='teachers.TeacherProfile'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='sat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sats', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='sun',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suns', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='thr',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='thrs', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='tue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tues', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancerule',
            name='wed',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weds', to='regulations.AttendanceTime'),
        ),
        migrations.AddField(
            model_name='attendancemembership',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regulations.AttendanceRule'),
        ),
        migrations.AddField(
            model_name='attendancemembership',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.TeacherProfile'),
        ),
    ]
