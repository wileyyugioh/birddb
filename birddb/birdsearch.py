from .birdcache import BirdGeoCache
from .birdranker import BirdRanker, SearchData

class SearchError(ValueError):
    """ Thrown when invalid search data is passed to search """


class BirdSearcher:
    """ Class to search for birds given a passed in SearchData """
    def __init__(self):
        self._bgc = BirdGeoCache()
        self._br = BirdRanker()

    def search(self, sd):
        """ Searches the databases for most likely birds """
        # Assume search data already verified
        bird_data = self._bgc.get(sd.lat, sd.lon)
        if not bird_data:
            return None

        # Get each bird's ranking
        rankings = self._br.batch_rank(sd, bird_data[0], bird_data[1])

        # Sort the rankings from highest to lowest
        rankings.sort(key=lambda tup: tup[1], reverse=True)

        return rankings