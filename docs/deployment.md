## Deployment

### Prerequisites
- Git
- Nginx
- Python3.6 or above
- Pip and Virtualenv
- Postgresql 11 or above

> Now CI/CD is not implemented in this project

### Prerequisites Installation
- Git
    ```
    sudo apt-get install git
    ```
- Nginx
    ```
    sudo apt-get install nginx
    ```

### Pip and Virtualenv Installation
- Pip Installation
    ```
    sudo apt -y install python3-venv python3-pip
    python3 -m pip install -U pip
    ```
    > Please restart the os in order for pip to work properly

- Virtualenv Installation
    ```
    python3 -m pip install virtualenv
    ```

### Postgresql Installation & Configuration
- Installation

    Please refer to this [link](https://www.postgresql.org/download/) to install Postgresql
    ```
    apt install libpq-dev
    ```

- Configuration

    ```
    sudo su postgres
    psql
    CREATE DATABASE database_name;
    CREATE USER my_username WITH PASSWORD 'my_password';
    GRANT ALL PRIVILEGES ON DATABASE "database_name" to my_username;
    ```

### Clone and installing project into local
> CI/CD is not implemented in this project
- Clone project 
    ```
    git clone https://github.com/lifelonglearner127/university-management.git
    cd university-management
    ```
- Install Build Packages
    ```
    apt install cmake
    apt install libsm6 libxext6 libxrender-dev
    ```
- Creating Virtual environment and configure `.env`
    ```
    python3 -m venv schools
    source schools/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    ```
    > Please make sure you install `cmake` in order to install `dlib` 

- Migrate and Create super user
    ```
    python manage.py collectstatic
    python manage.py migrate
    python manage.py createsuperuser
    ```

## Instsall RabbitMQ
    ```
    apt install rabbitmq-server
    ```

## Configure Redis as docker
    ```
    apt install docker.io
    docker run -dit --restart unless-stopped -p 6379:6379 -d redis:2.8
    ```

### Running `uwsgi` and `daphne` service
- Running Gateway Interface on Local
    ```
    sudo cp deploy/university-backend.conf /etc/nginx/sites-available
    sudo ln -s /etc/nginx/sites-available/university-backend.conf /etc/nginx/sites-enabled/university-backend.conf 
    daphne --port 9000 --verbosity 1 config.asgi:application
    uwsgi --ini deploy/university_backend.ini
    ```

- Change some settings
    - Changes in `deploy/schools_daphne.service`
        - change `WorkingDirectory`
        - change `Environment`
        - change `ExecStart`
    - Changes in `deploy/schools_uwsgi.service`
        - change `Environment`
        - change `ExecStart`
    - Changes in `deploy/university_backend.ini`
        - change `chdir`
        - change `chown-socket`
    - Changes in `config/settings/staging.py`
        - change `ALLOWED_HOSTS`
        - change `CORS_ORIGIN_WHITELIST`

- Making Service
    ```
    cp deploy/*.service /lib/systemd/system/
    systemctl daemon-reload
    systemctl restart/status/enable schools_uwsgi.service
    systemctl restart/status/enable schools_daphne.service
    systemctl restart/status/enable schools_celery.service
    systemctl restart/status/enable schools_celerybeat.service
    ```
