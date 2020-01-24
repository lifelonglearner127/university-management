## Development
- [Setting Development Environment](#setting-development-environment)
- [Commands](#commands)

### Setting Development Environment
#### Prerequisites
- Git
- Python3.6 or above
- Virtualenv
- Postgresql 11 or above

#### Postgresql Installation & Configuration
- Installation

    Please refer to this [link](https://www.postgresql.org/download/) to install Postgresql

- Configuration

    ```
    sudo su postgres
    psql
    CREATE DATABASE database_name;
    CREATE USER my_username WITH PASSWORD 'my_password';
    GRANT ALL PRIVILEGES ON DATABASE "database_name" to my_username;
    ```

#### Clone and installing project into local
- Clone project 
    ```
    git clone https://github.com/lifelonglearner127/university-management.git
    cd university-management
    ```

- Creating Virtual environment
    ```
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

- Migrate and Run
    ```
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
    ```

### Commands
- Saving db data to fixture file
    ```
    python manage.py dumpdata [app_label[.ModelName] [app_label[.ModelName] ...]]

    python manage.py dumpdata accounts.User accounts.UserPermission accounts.Permission --indent 4 --output fixtures/accounts.json
    
    python manage.py dumpdata contents.Advertisement contents.AdvertisementAudiences contents.Notification contents.NotificationAudiences --indent 4 --output fixtures/contents.json
    
    python manage.py dumpdata regulations.AttendancePlace regulations.TimeSlot regulations.AttendanceTime regulations.AttendanceRule regulations.AttendanceMembership regulations.UnAttendanceMembership regulations.AttendanceEvent regulations.AttendanceHistory --indent 4 --output fixtures/regulations.json

    python manage.py dumpdata teachers.Department teachers.Position teachers.TeacherProfile teachers.TeacherImage --indent 4 --output fixtures/teachers.json
    ```

- Providing data with fixtures
    ```
    python manage.py loaddata fixtures/accounts.json
    python manage.py loaddata fixtures/contents.json
    python manage.py loaddata fixtures/regulations.json
    python manage.py loaddata fixtures/teachers.json
    ```

- DB Dump
    ```
    pg_dump -U school_dev -h localhost schools -a -F p -f backups/dump.sql

    psql -U school_dev -d schools -f dump.sql
    ```