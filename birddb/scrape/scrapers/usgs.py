from requests import get, Response
from re import IGNORECASE, search, sub

class UsgsScraper:
    """ Scrapes the Patuxent Bird Identification InfoCenter """
    def __init__(self):
        self._raw_page = None

    def _load_table_of_contents(self):
        """ Load the base page """
        HEAD_URL = "https://www.mbr-pwrc.usgs.gov/id/framlst/"
        self._raw_page = get(HEAD_URL).text

    def get_identification(self, scientific_name):
        """ Returns the identification tips """

        REGEX_PAGE = '<li>.*href="(.*?)".*?<em>{} <\/em>'
        custom_regex = REGEX_PAGE.format(scientific_name)

        if not self._raw_page:
            self._load_table_of_contents()

        r = search(custom_regex, self._raw_page, flags=IGNORECASE)

        if not r:
            return None

        ID_URL = "https://www.mbr-pwrc.usgs.gov/id/framlst/Idtips/{}"

        # Replace the first character from i to h
        new_tag = r.group(1)
        new_tag = 'h' + new_tag[1:]

        custom_id = ID_URL.format(new_tag)
        raw_id = get(custom_id).text

        # Find the identification tips paragraph
        REGEX_ID = "Identification Tips:([\s\S]*)Similar species:"
        r_id = search(REGEX_ID, raw_id)

        if not r_id:
            return None

        # Strip html tags
        REGEX_HTML = "<.*?>"
        r_strip = sub(REGEX_HTML, "", r_id.group(1))

        return r_strip.strip()


# Debug
if __name__ == "__main__":
    from time import time
    start = time()
    us = UsgsScraper()
    id_text = us.get_identification("Gymnogyps californianus")
    print(id_text.split("\n")[0])
    print("Elapsed time: ", time() - start)
