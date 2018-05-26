from os import environ


try:
    EBIRD_API_KEY = environ["EBIRD_KEY"]
except KeyError:
    EBIRD_API_KEY = ""