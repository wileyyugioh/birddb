from requests import get, Response

try:
    from .ebirdconfig import EBIRD_API_KEY
except ImportError:
    from ebirdconfig import EBIRD_API_KEY


class EbirdScraper:
    """ Uses the eBird 2.0 API to get birds given a location """

    # EBIRD_API_KEY needs to be imported from a separate config file
    HEADERS = {"X-eBirdApiToken": EBIRD_API_KEY}

    def get_recent_obs_raw(self, locid, lon=None):
        """ Given locid / lat & lon, return all the birds observed recently there """
        custom_url = ""

        if not lon:
            # If passed in a locid
            BASE_URL = "https://ebird.org/ws2.0/data/obs/{}/recent?back=30"
            custom_url = BASE_URL.format(locid)
        else:
            # If passed in a latitude and longitude we use a different url
            BASE_URL = "https://ebird.org/ws2.0/data/obs/geo/recent?lat={}&lng={}&back=30"
            custom_url = BASE_URL.format(locid, lon)

        response = get(custom_url, headers=EbirdScraper.HEADERS)

        return response.json()

    def get_recent_obs(self, locid, lon=None):
        """ get_recent_obs_raw formatted to return a list of sci names"""
        SCI_NAME_CODE = "sciName"
        FREQUENCY_CODE = "howMany"
        raw_data = self.get_recent_obs_raw(locid, lon)
        sci_names = [None] * len(raw_data)
        for i, entry in enumerate(raw_data):
            try:
                frequency = entry[FREQUENCY_CODE]
            except KeyError:
                frequency = 1

            sci_names[i] = (entry[SCI_NAME_CODE].lower(), frequency)

        return sci_names

# Debug
if __name__ == "__main__":
    es = EbirdScraper()
    SF_birds = es.get_recent_obs("US-CA-075")
    print(SF_birds[0])