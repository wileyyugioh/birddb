try:
    from .scrape.colornames import color_distance_norm, SIMPLIFIED_COLORS_NAMES
except ImportError:
    from scrape.colornames import color_distance_norm, SIMPLIFIED_COLORS_NAMES

from math import log


class SearchData:
    """ Wrapper for search query data """
    def __init__(self, lati, longi, color, size):
        self.lat = lati
        self.long = longi
        self.color = color
        self.size = size

    def valid(self):
        """ Returns True if all data is not None """
        return (bool((self.lat and
                      self.long and
                      self.color and
                      self.size
                    )) and
                (-90 <= self.lat <= 90) and
                (-180 <= self.long <= 180) and
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

    def _size_dist(sizea, sizeb):
        """ Returns the distance from the size bracket """
        def get_bracket(size, i=0):
            if i < BirdRanker.SIZES_SIZE and size > BirdRanker.SIZES[i][0]:
                return get_bracket(size, i + 1)
            return i

        if sizeb == None:
            return BirdRanker.SIZES_SIZE // 2

        return abs(get_bracket(sizea) - get_bracket(sizeb))


    def rank(self, sd, bird, frequency):
        """ Gives a bird a score compared to how close it is to sd """
        COLOR_MULTIPLIER = 9.0
        SIZE_MULTIPLIER = 5.0
        FREQUENCY_MULTIPLIER = 1.0

        color = bird.get_color()
        if not color:
            return 0

        size = bird.get_size()

        color_dist = color_distance_norm(sd.color, color)

        size_dist = BirdRanker._size_dist(sd.size, size)

        # Super secret algorithms and math!
        score = ((1.0 - color_dist) * COLOR_MULTIPLIER + 
                 (BirdRanker.SIZES_SIZE - size_dist) * SIZE_MULTIPLIER +
                 log(frequency, 10) * FREQUENCY_MULTIPLIER
                )

        return score