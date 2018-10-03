# Repo. for Birddb

![Title Image]('resources/title.png')

Since my hosting credit ran dry, here is the source.

## Notes on deploying the server

Need to mess around with xenocano/settings.py to get ready for prod.

You also need to set the enviroment variable `DJANGO_KEY`

Recommendations:

Set DEBUG to FALSE in settings.py

Enable Template Caching

Set up other database, like postgres

### FOLLOW THESE EXTREMELY LIMITED STEPS AT YOUR OWN RISK

## A quick guide for quick set up (don't run on prod. before doing above steps)

```
python manage.py createcachetable
python manage.py collectstatic
DJANGO_KEY='MYCOOLKEY' python manage.py runserver
```
