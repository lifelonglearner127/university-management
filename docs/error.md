## Error Reporting
- Why don't we set debug mode on production site?
    - It is possible, but debug mode often causes memory leaks, and it has some vulnerability on security.
    - Raw error can be seen on user side

- Possible to track the error?
    - Of course, yes. That is why the [Sentry](https://sentry.io/) come in.
    - Just follow this [link](https://docs.sentry.io/platforms/python/django/).
    - It support 3 membership but free plan is enough for such a simple project.
