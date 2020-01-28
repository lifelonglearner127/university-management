# University Management
- [Docs](#docs)
- [FAQ](#faq)

## Docs
- [Project](docs/project.md)

    This document describes how our project is composed based on project functionalities

- [Development](docs/development.md)

    - This document describes how to setup local development environment step by step.
    - This document also describe some django admin commands that is useful in the development

- [Postman](docs/postman.md)

    - You can see the `postman` directory in the project root level. This contains the api files exported as json from Postman.
    - You need to import these files to Postman for testing apis on either local or stating.
    - It might be helpful to create an evironment variable on Postman for better switching local and staging.
    - Do not test these api on the production server.

- [Deployment](docs/deployment.md)

    - This document describes how to deploy the project to local or cloud server step by step.
    - Not only that, it also contains some custom scripts running on the server like `db backup`

- [Face Recognition](docs/face-recognition.md)

    This document describes the latest face recognition methods and why our choice is superior to others.

- [Error Reporting](docs/error.md)

    This document describles the methodology how we can track the bug on production site.

## FAQ
1. Why do you use Django 2.2.1?

    I tried to upgrade to django 3, but auto reboot broke after upgrade. Encountered such error `django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async`. I found an article in the documentation (https://docs.djangoproject.com/en/3.0/topics/async/#async-safety), but I don’t understand how to fix the problem?
    