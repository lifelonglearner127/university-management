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
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo apt-get install python3-distutils
    python3 get-pip.py --user
    ```
    > Please restart the os in order for pip to work properly

- Virtualenv Installation
    ```
    pip install virtualenv --user
    ```

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
> CI/CD is not implemented in this project
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

- Migrate and Create super user
    ```
    python manage.py collectstatic
    python manage.py migrate
    python manage.py createsuperuser
    ```