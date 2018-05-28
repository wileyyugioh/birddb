from .scrape.colornames import color_distance_norm, SIMPLIFIED_COLORS_NAMES

class SearchData:
    """ Wrapper for search query data """
    def __init__(self, lati, longi, color, size):
        self.lat = lati
        self.lon = longi
        self.color = color
        self.size = size

    def valid(self):
        """ Returns True if all data is not None """
        return (bool((self.lat and
                      self.lon and
                      self.color and
                      self.size
                    )) and
                (-90 <= self.lat <= 90) and
                (-180 <= self.lon <= 180) and
                (self.color in SIMPLIFIED_COLORS_NAMES) and
                (self.size > 0)
               )



class BirdRanker:
    """ When given a SearchData, ranks birds compared to it """
    SIZES = ((7.6, 12.7),
             (12.7, 22.86),
             (22.86, 40.64),
             (40.64, 81.28),
             (81.28, 182.88)
            )
    SIZES_SIZE = len(SIZES)

    COLOR_MULTIPLIER = 9.0
    SIZE_MULTIPLIER = 5.0
    FREQUENCY_MULTIPLIER = 0.01

    def _size_dist(sizea, sizeb):
        """ Returns the distance from the size bracket """
        def get_bracket(size, i=0):
            if i < BirdRanker.SIZES_SIZE and size > BirdRanker.SIZES[i][0]:
                return get_bracket(size, i + 1)
            return i

        if sizeb is None:
            return BirdRanker.SIZES_SIZE // 2

        return abs(get_bracket(sizea) - get_bracket(sizeb))

    def _score(sd, color, size, frequency):
        """ Returns a numerical score """

        color_dist = color_distance_norm(sd.color, color)
        size_dist = BirdRanker._size_dist(sd.size, size)

        # Super secret algorithms and math!
        score = ((1.0 - color_dist) * BirdRanker.COLOR_MULTIPLIER + 
                 (BirdRanker.SIZES_SIZE - size_dist) * BirdRanker.SIZE_MULTIPLIER +
                 frequency * BirdRanker.FREQUENCY_MULTIPLIER
                )
        return score

    def rank(self, sd, bird, frequency):
        """ Gives a bird a score compared to how close it is to sd """
        color = bird.get_color
        if not color:
            return 0

        size = bird.get_size

        return BirdRanker._score(sd, color, size, frequency)

    def batch_rank(self, sd, complete):
        """ Batch ranks, hopefully caching Django queries """
        size = len(complete)
        full = [None] * size
        for i in range(size):
            color = complete[i][0].get_color
            if color:
                size = complete[i][0].get_size
                score = BirdRanker._score(sd, color, size, complete[i][1])
            else:
                score = 0

            full[i] = (complete[i][0], score)
        return full