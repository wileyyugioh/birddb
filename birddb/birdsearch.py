try:
    from .birdaccess import BirdAccess
    from .birdranker import BirdRanker, SearchData
    from .scrape.scrapers.ebird import EbirdScraper
except ImportError:
    from birdaccess import BirdAccess
    from birdranker import BirdRanker, SearchData
    from scrape.scrapers.ebird import EbirdScraper


class SearchError(ValueError):
    """ Thrown when invalid search data is passed to search """


class BirdSearcher:
    """ Class to search for birds given a passed in SearchData """
    def __init__(self):
        self._eb = EbirdScraper()
        self._br = BirdRanker()
        self._ba = BirdAccess()

    def search(self, sd):
        """ Searches the databases for most likely birds """

        # Assume search data already verified

        # Get a list of birds given the geographical location
        birds_geo = self._eb.get_recent_obs(sd.lat, sd.long)

        # Get a list of BirdData
        bird_data = self._ba.batch_soft_get_bird([bird[0] for bird in birds_geo])

        # Get each bird's ranking
        rankings = []
        for i in range(len(bird_data)):
            if bird_data[i]:
                rankings.append((bird_data[i], self._br.rank(sd, bird_data[i], birds_geo[i][1])))

        # Sort the rankings from highest to lowest
        rankings.sort(key=lambda tup: tup[1], reverse=True)

        return rankings