from django.core.cache import cache
from django.db.models import Prefetch, prefetch_related_objects

from .models import Bird

from .birdaccess import BirdAccess, TooLongError
from .scrape.scrapers.ebird import EbirdScraper

from threading import Thread

from time import time


class BirdGeoCache:
    """ Caches birds given a geolocation """
    def __init__(self):
        self._ba = BirdAccess()
        self._eb = EbirdScraper()

    def _do_add_cache(async_result, freq, cache_key, cache_time):
        """ This runs in a thread """
        result = async_result.get()
        BirdGeoCache._process_and_cache(result, freq, cache_key, cache_time)

    def _add_cache_when_done(async_result, freq, cache_key, cache_time):
        """ Title """
        thread = Thread(target=BirdGeoCache._do_add_cache, args=(async_result, freq, cache_key, cache_time))
        thread.start()

    def _process_and_cache(birds, freq, cache_key, cache_time):
        """ Processes Bird and frequency data, and caches it """

        all_birds = []
        all_freq = []
        for i in range(len(birds)):
            if birds[i]:
                all_birds.append(birds[i])
                all_freq.append(freq[i])

        complete = (all_birds, all_freq)
        cache.set(cache_key, complete, cache_time)
        return complete

    def get(self, lat, lon, cache_time=12*60*60):
        """ Returns birds at latitude and longitude """
        # Remember to, round it
        # .01 deg ~ .689 mi, so close enough
        cache_key = "{:.2f}{:.2f}".format(lat, lon)
        complete = cache.get(cache_key)

        if complete is None:
            birds_geo = self._eb.get_recent_obs(lat, lon)
            raw_birds, raw_freqs = zip(*birds_geo)

            # Get a list of BirdData
            birds, success = self._ba.batch_soft_get_bird(raw_birds)
            if not success:
                BirdGeoCache._add_cache_when_done(bird_data, raw_freqs, cache_key, cache_time)
                raise TooLongError()
            complete = BirdGeoCache._process_and_cache(birds, raw_freqs, cache_key, cache_time)

        # Let's profile!
        start = time()
        prefetch_related_objects([bird for bird in complete[0] if not bird.size], "genus")
        prefetch_related_objects(complete[0], "birdpollcolor_set")
        print("PREFETCH", time() - start)
        return complete