Repo. for Birddb

Need to mess around with settings.py to get ready for prod.

Recommendations:

Turn off DEBUG

Enable Template Caching

Set up other database

???

## A quick guide for quick set up (don't run on prod. before doing above steps)

```
python manage.py createcachetable
python manage.py collectstatic
```
