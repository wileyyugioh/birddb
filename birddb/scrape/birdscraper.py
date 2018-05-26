import re

try:
    from . import colornames
    from .scrapers import gbif, usgs, xenocanto, wikipedia
except ImportError:
    import colornames
    from scrapers import gbif, usgs, xenocanto, wikipedia


class BirdScraper_Not_A_Bird(ValueError):
    """ Error thrown when the animal passed to BirdScraper is not a bird """


class BirdData:
    """ Returned by BirdScraper """
    def __init__(self, sci_name, genus, common_names, color, sizes):
        self.sci_name = sci_name.lower() if sci_name else sci_name
        self.genus = genus.lower() if genus else genus
        # common names is lowered earlier :( bad code...
        self.common_names = common_names
        self.color = color.lower() if color else color
        self.sizes = sizes

    def __str__(self):
        return self.sci_name

    def success(self):
        """ All data (except size and color) is valid """
        return bool((self.sci_name and
                     self.genus and
                     self.common_names
                   ))

    def get_size_avg(self):
        """ Return the average size of the bird """
        if self.sizes:
            if len(self.sizes) == 1:
                return self.sizes[0]
            elif len(self.sizes) == 2:
                return (self.sizes[0] + self.sizes[1]) / 2
        return None


class BirdDataExtra:
    """ Returned by BirdScraper.scrape_extra(?) """
    def __init__(self, img, img_rec, img_lic, call, rec, license):
        self.img = img if img else ""
        self.img_rec = img_rec if img_rec else ""
        self.img_lic = img_lic if img_lic else ""
        self.call = call if call else ""
        self.call_rec = rec if rec else ""
        self.call_lic = license if license else ""


class BirdScraper:
    """ Finds all the wanted data of a bird by scraping the web """
    _sizebackup_regex = re.compile("(\d[\d|\.]*)(?:\sto\s|–)([\d|\.]*\s)(?:cm|centimet(?:re|er)s)").search
    _single_regex = re.compile("(\d[\d|\.]*\s)(?:cm|centimet(?:re|er)s)").search
    _find_size_regex = re.compile("Length:\s*([\d\.]+) inches").search
    _sci_regex = re.compile("\(<i>([^<]*)</i>\)").search
    _bold_regex = re.compile("<b>([^<]*)<\/b>").findall

    def _find_genus(self, sci_name):
        """ Basically extracts the first word of the scientific name """
        sci_split = sci_name.split()
        return sci_split[0]

    def _find_color(self, desc_text):
        """ Finds the color of the bird given a wikipedia description """
        return colornames.find_color(desc_text)

    def _find_sizebackup(self, desc_text):
        """ Find the size of the bird given a wikipedia description """
        size = None

        # TODO: Make sure we don't get wingspan...
        # TODO: Add support for big birds (size in meters)
        # TODO: What happens when the size can't be found...?
        # Generally, the size of a bird is given as a range...
        # RANGE_REGX = "(\d[\d|\.]*)(?:\sto\s|–)([\d|\.]*\s)(?:cm|centimet(?:re|er)s)"
        r = BirdScraper._sizebackup_regex(desc_text)
        if r:
            small_range = float(r.group(1))
            # Slap on [:-1] to remove space
            large_range = float(r.group(2)[:-1])

            size = [small_range, large_range]
        else:
            # However, if we can't find a range use any size we can get
            # SINGLE_REGEX = "(\d[\d|\.]*\s)(?:cm|centimet(?:re|er)s)"
            r = BirdScraper._single_regex(desc_text)
            if r:
                extract_size = float(r.group(1))
                size = [extract_size]

        return size

    def _find_size(self, sci_name):
        """ Find the size using USGS site """
        cm_length = None

        us = usgs.UsgsScraper()
        id_text = us.get_identification(sci_name)

        if not id_text:
            return None

        # LENGTH_REGEX = "Length:\s*([\d\.]+) inches"
        r = BirdScraper._find_size_regex(id_text)

        if r:
            # Remember that the length here is in inches
            # We want cm!
            in_length = float(r.group(1))
            cm_length = in_length * 2.54

        return [cm_length]

    def _find_names(self, summ_text, sci_name):
        """ Find the scientific common names of a bird using wikipedia """
        # Scientific names are the first words in parentheses
        # SCI_REGEX = "\(<i>([^<]*)</i>\)"
        r = BirdScraper._sci_regex(summ_text)

        if r:
            # We can find a scientific name in wikipedia
            sci_name = r.group(1)

        # The secret is that the common names of a bird is bolded
        # BOLD_REGEX = "<b>([^<]*)<\/b>"
        names = [name.lower() for name in BirdScraper._bold_regex(summ_text)]

        return sci_name, names

    def scrape(self, sci_name):
        """ Scrape the web to find colors and size """
        # Here's the wikipedia part
        DESCRIPTION_HEADER = "Description"
        ws = wikipedia.WikipediaScraper()
        try:
            raw_summary = ws.get_raw_summary(sci_name)
            desc_text = ws.get_section(sci_name, DESCRIPTION_HEADER)
        except Exception:
            raise BirdScraper_Not_A_Bird("Failed to find Wikipedia article")

        # Fallback to summary text if no description section
        if not desc_text:
            desc_text = raw_summary

        # Find the bird's names / aliases
        sci_name, common_names = self._find_names(raw_summary, sci_name)

        # Now that we know we have the true scientific name, extract genus
        genus = self._find_genus(sci_name)

        # Find the bird's main colors
        color = self._find_color(desc_text)

        # Use USGS to find sizes (only works in US)
        sizes = self._find_size(sci_name)

        # Fallback for size to wikipedia if USGS fails
        # This generally happens if the bird is not found in the US
        if not sizes:
            sizes = self._find_sizebackup(desc_text)

        # If not in the description, try in the article summary
        if not sizes:
            sizes = self._find_sizebackup(raw_summary)

        return BirdData(sci_name, genus, common_names, color, sizes)

    def scrape_extra(self, sci_name):
        """ Scrape the web for extra resources """
        ws = wikipedia.WikipediaScraper()
        xs = xenocanto.XenocantoScraper()

        try:
            img, img_rec, img_lic = ws.get_image(sci_name)
        except:
            img = None
            img_rec = None
            img_lic = None

        try:
            call, rec, lic  = xs.get_by_name(sci_name)
        except:
            call = None
            rec = None
            lic = None
        return BirdDataExtra(img, img_rec, img_lic, call, rec, lic)


# Debug
if __name__ == "__main__":
    from time import time
    start = time()
    cc = BirdScraper()
    #data = cc.scrape("gymnogyps californianus")
    data = cc.scrape("Phalacrocorax pelagicus")
    print("Scraping success: Yes!")
    print(data)
    print(data.common_names)
    print(data.color)
    print(data.sizes)
    print("Elapsed time: {}".format(time() - start))
