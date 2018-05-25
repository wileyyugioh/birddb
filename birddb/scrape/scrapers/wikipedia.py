from requests import get, Response
from re import search

# TODO: What happens when an invalid article is given?

class WikipediaScraper:
    """ Uses the Wikipedia API to get summary and data """

    def __init__(self):
        # Cache the last request
        self._prev_url = None
        self._prev_data = None

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

        r = search(custom_regex, raw_page)

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
        custom_url = BASE_URL.format(title_name, size)

        response = get(custom_url)
        json_data = response.json()

        wiki_data = next(iter(json_data["query"]["pages"].values()))

        return wiki_data["thumbnail"]["source"]


# Debug
if __name__ == "__main__":
    ws = WikipediaScraper()
    title = ws.get_title("Gymnogyps californianus")
    print(title)
    img = ws.get_image("Gymnogyps californianus")
    print(img)
