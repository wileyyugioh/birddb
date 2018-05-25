from requests import get, Response


class GbifScraper:
    """ Uses the GBIF Api to find taxonomic data """

    def get_class(self, sci_name):
        """ Returns the class of the given animal """
        BASE_URL = "http://api.gbif.org/v1/species?name="
        custom_url = BASE_URL + sci_name

        response = get(custom_url)
        json_data = response.json()

        sci_class = json_data["results"][0]["class"]

        return sci_class


if __name__ == "__main__":
    gs = GbifScraper()
    hopefully_aves = gs.get_class("Gymnogyps californianus")
    print(hopefully_aves)
