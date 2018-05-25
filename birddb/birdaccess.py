from django.db import IntegrityError

from .models import Bird, BirdReference, Genus, InvalidBird, WebData

from .scrape.birdscraper import BirdScraper

from functools import partial
from multiprocessing import TimeoutError
from multiprocessing.pool import ThreadPool
from random import uniform
from time import time, sleep


class EntryError(ValueError):
    """ Raised in soft_get_bird """


class TooLongError(RuntimeError):
    """ Raised when loading birds took too long """


class BirdAccess:
    """ Class for accessing bird data """
    def __init__(self, threads=True):
        self._is_threading = True
        self._bs = BirdScraper()
        self._thread_func = partial(BirdAccess._do_soft_get_bird, self._bs)


    def _do_soft_get_bird(bs, sci_name):
        """ Returns a bird entry in the database. Creates an entry if it doesn't exist """

        # Assumes sci_name is all lower case
        # Check for BirdReference
        try:
            bird = BirdReference.objects.get(sci_name__exact=sci_name).bird
            return bird
        except BirdReference.DoesNotExist:
            pass

        # Check to see if the bird is invalid
        if InvalidBird.objects.filter(sci_name__exact=sci_name).exists():
            return None

        try:
            data = bs.scrape(sci_name)
            if not data.success():
                raise EntryError("Failed to scrape")
        except Exception as e:
            print(e)
            InvalidBird.objects.get_or_create(sci_name=sci_name)
            return None

        # See if Bird already exists, if so, then create new BirdReference
        try:
            bird = Bird.objects.get(sci_name__iexact=data.sci_name)
            BirdReference.objects.get_or_create(sci_name=sci_name,
                                                bird=bird
                                               )
            return bird
        except Bird.DoesNotExist:
            pass

        # After here, we assume that we encountered a brand new Bird

        # Create a WebData object
        extra = bs.scrape_extra(data.sci_name)
        while True:
            try:
                genus = Genus.objects.get_or_create(name=data.genus)[0]

                web_data = WebData.objects.get_or_create(img=extra.img,
                                                         call=extra.call
                                                        )[0]

                # Create a new bird object
                bird = Bird.objects.get_or_create(name=",".join(data.common_names),
                                                  sci_name=data.sci_name,
                                                  genus=genus,
                                                  color=data.color,
                                                  size=data.get_size_avg(),
                                                  web_data=web_data
                                                 )[0]

                # Add the birdonym
                BirdReference.objects.get_or_create(sci_name=sci_name,
                                                    bird=bird
                                                   )
                return bird
            except IntegrityError as e:
                # Chill dude!
                sleep(uniform(0.1, 0.5))

    def soft_get_bird(sci_name, bs=BirdScraper()):
        """ Wrap _do_soft_get_bird """
        return BirdAccess._do_soft_get_bird(bs, sci_name)

    def batch_soft_get_bird(self, sci_names):
        """ When passed in a list of bird names, returns a list of bird entries """
        if not self._is_threading:
            bs = BirdScraper()
            birds_len = len(sci_names)
            birds = [None] * birds_len
            for i, name in enumerate(sci_names):
                birds[i] = soft_get_bird(name, bs)
        else:
            tp = ThreadPool()
            async_result = tp.map_async(self._thread_func, sci_names)
            try:
                birds = async_result.get(timeout=10)
            except TimeoutError:
                raise TooLongError()

        return birds