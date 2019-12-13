## Development

### Prerequisites
- Git
- Python3.6 or above
- Virtualenv
- Postgresql 11 or above

### Postgresql Installation & Configuration
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

### Clone and installing project into local
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