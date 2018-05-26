from requests import get, Response

try:
    from .helpers import convertToHttps
except ImportError:
    from helpers import convertToHttps

class XenocantoScraper:
    """ Uses the Xenocanto API to snag audio """
    URL_PATH = "https://www.xeno-canto.org/api/2/recordings?query="
    def get_by_name(self, name):
        """ Return a url of a grade A audio clip of bird name """
        custom_url = XenocantoScraper.URL_PATH + name + " q:A"
        response = get(custom_url)
        json_data = response.json()

        recordings = json_data["recordings"]

        # Return first recording audio url
        if recordings:
            return convertToHttps(recordings[0]["file"][2:]), recordings[0]["rec"], convertToHttps(recordings[0]["lic"][2:])
        return None, None, None


if __name__ == "__main__":
    xs = XenocantoScraper()
    audio_url, rec, lic = xs.get_by_name("Apus apus")
    print(audio_url, rec, lic)