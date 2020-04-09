from celery.schedules import crontab


broker_url = 'amqp://localhost'
beat_schedule = {
    'update_date_person_report': {
        'task': 'apps.regulations.tasks.update_attendance_report',
        'schedule': crontab(minute=0, hour=2),
    },
}

task_always_eager = True
