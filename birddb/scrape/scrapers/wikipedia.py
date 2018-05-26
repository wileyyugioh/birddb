import re

from requests import get, Response
from urllib.parse import quote

try:
    from .helpers import convertToHttps
except ImportError:
    from helpers import convertToHttps


class WikipediaScraper:
    """ Uses the Wikipedia API to get summary and data """
    sub_href_regex = re.compile('href="([^\"]+)"').sub

    def __init__(self):
        # Cache the last request
        self._prev_url = None
        self._prev_data = None

    def _replace_href_with_https(raw_text):
        """ Converts href into https equivalent """
        def format(matcharoni):
            return 'href="' + convertToHttps(matcharoni.group(1)) + '"'
        return WikipediaScraper.sub_href_regex(format, raw_text)

    def _summary_base(self, title_name, base_url):
        """ The base function for getting a summary """
        if base_url == self._prev_url:
            return self._prev_data

        custom_url = base_url + title_name.replace(" ", "_")

        response = get(custom_url)
        json_data = response.json()

        wiki_data = next(iter(json_data["query"]["pages"].values()))

        self._prev_url = base_url
        self._prev_data = wiki_data

        return wiki_data

    def get_summary(self, title_name):
        """ Return text of summary """
        BASE_URL = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&action=query&prop=extracts&exintro=&explaintext=&titles="
        return self._summary_base(title_name, BASE_URL)["extract"]

    def get_raw_summary(self, title_name):
        """ Return text of summary with markup """
        BASE_URL = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&action=query&prop=extracts&exintro=&titles="
        return self._summary_base(title_name, BASE_URL)["extract"]

    def get_section(self, title_name, section_name):
        """ Return text of section """

        REGEX_EXP = "{} ==((?:.|\n)*?)(?:==|$)"
        custom_regex = REGEX_EXP.format(section_name)

        BASE_URL = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&action=query&prop=extracts&explaintext=&titles="
        raw_page = self._summary_base(title_name, BASE_URL)["extract"]

        r = re.search(custom_regex, raw_page)

        if not r:
            return None

        # strip the newlines
        return r.group(1).replace("\n", "")

    def get_title(self, title_name):
        """ Returns the title of a redirected page """
        BASE_URL = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&action=query&prop=extracts&exintro=&explaintext=&titles="
        return self._summary_base(title_name, BASE_URL)["title"]

    def get_image(self, title_name, size=400):
        """ Returns the url of thumbnail image """
        BASE_URL = "https://en.wikipedia.org/w/api.php?action=query&redirects=1&titles={}&prop=pageimages&format=json&pithumbsize={}"
        LICENSE_URL = "https://en.wikipedia.org/w/api.php?action=query&redirects=1&titles=File:{}&prop=imageinfo&iiprop=extmetadata&format=json"
        custom_url = BASE_URL.format(title_name, size)

        response = get(custom_url)
        json_data = response.json()

        wiki_data = next(iter(json_data["query"]["pages"].values()))

        file_name = quote(wiki_data["pageimage"])

        custom_license_url = LICENSE_URL.format(file_name)

        response = get(custom_license_url)
        json_data = response.json()

        license_data = next(iter(json_data["query"]["pages"].values()))["imageinfo"][0]["extmetadata"]

        try:
            try:
                artist = license_data["Attribution"]["value"]
            except KeyError:
                artist = license_data["Artist"]["value"]

            artist = WikipediaScraper._replace_href_with_https(artist)

            # max_len is defined in charfield to be ~400
            MAX_LEN = 400
            if len(artist) > MAX_LEN: raise ValueError("Artist too long") 
        except Exception:
            artist = "<a href='https://commons.wikimedia.org/wiki/File:{}'>Unknown Author</a>".format(file_name)

        try:
            license_name = license_data["LicenseShortName"]["value"]
            license_href = convertToHttps(license_data["LicenseUrl"]["value"])
        except KeyError:
            license_name = license_data["LicenseShortName"]["value"]
            license_href = ""

        return wiki_data["thumbnail"]["source"], artist, license_name, license_href


# Debug
if __name__ == "__main__":
    ws = WikipediaScraper()
    title = ws.get_title("Gymnogyps californianus")
    print(title)
    #img, art, lic, href = ws.get_image("Gymnogyps californianus")
    img, art, lic, href = ws.get_image("Calidris canutus")
    print(img)
    print(art)
    print(lic)
    print(href)
