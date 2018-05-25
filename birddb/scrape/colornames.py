from math import sqrt
import re


COLOR_VALUES = {
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "green": (0, 128, 0),
    "cyan": (0, 255, 255),
    "blue": (0, 0, 255),
    "indigo": (111, 0, 255),
    "violet": (159, 0, 255),
    "purple": (128, 0, 128),
    "magenta": (255, 0, 255),
    "pink":  (255, 192, 203),
    "brown": (165, 42, 42),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "black": (0, 0, 0),
    "rufous": (168, 28, 7),
    "maroon": (128, 0, 0),
    "emerald": (39, 89, 45)
}
COLOR_NAMES = list(COLOR_VALUES.keys())

RAW_SIMPLIFIED_COLORS = {
    "red": ["pink", "rufous"],
    "orange": [""],
    "yellow": [""],
    "green": ["emerald"],
    "blue": ["cyan"],
    "violet": ["indigo", "magenta"],
    "brown": ["maroon"],
    "grey": ["gray"],
    "white": [""],
    "black": [""]
}

SIMPLIFIED_COLORS_NAMES = list(RAW_SIMPLIFIED_COLORS.keys())
SIMPLIFIED_COLORS = {}
for k, v in RAW_SIMPLIFIED_COLORS.items():
    for color in v:
        SIMPLIFIED_COLORS[color] = k
    SIMPLIFIED_COLORS[k] = k


def simplify_color(color):
    """ Simplifies a color using our SIMPLIFIED_COLORS dictionary """
    return SIMPLIFIED_COLORS[color]


def color_distance_raw(a, b):
    """ Returns an estimate of the color distance by human perception """
    # Based on http://www.compuphase.com/cmetric.htm

    rmean = (a[0] + b[0]) / 2
    r = a[0] - b[0]
    g = a[1] - b[1]
    b = a[2] - b[2]

    return sqrt((2 + rmean / 256) * r**2 + 4 * g**2 + (2 + (255 - rmean) / 256) * b**2)


def color_distance(a, b):
    """ Pass in names instead """
    return color_distance_raw(COLOR_VALUES[a.lower()], COLOR_VALUES[b.lower()])

def color_distance_norm(a, b):
    """ Fit the color distance into [0, 1] """
    # Max calculated by distance between black and white
    MAX_VAL = 765
    return color_distance(a, b) / MAX_VAL


OPTIONAL_PREFIX = ["all"
                  ]
REGEX_BASE = "\ ({0}|{1})(?:ish)?(?:\-({0})(?:ish)?|[^\w\-])"
color_group = "|".join(COLOR_NAMES)
prefix_group = "|".join(OPTIONAL_PREFIX)
custom_regex = REGEX_BASE.format(color_group, prefix_group)
find_colors_regex = re.compile(custom_regex).findall


def find_color(data_string):
    """ Returns first color found in article """
    # Some problems is that it may not work with hybrid words (ex. 'greenish')
    for search_group in find_colors_regex(data_string):
        for color in search_group:
            if color and color in COLOR_VALUES:
                return simplify_color(color)

# Debug
if __name__ == "__main__":
    # Description taken from https://en.wikipedia.org/wiki/California_condor
    condor_desc = r"""The adult California condor is a uniform black with the exception of
                      large triangular patches or bands of white on the underside of the wings.
                      It has gray legs and feet, an ivory-colored bill, a frill of black feathers
                      surrounding the base of the neck, and brownish red eyes.
                      The juvenile is mostly a mottled dark brown with blackish coloration on the head.
                      It has mottled gray instead of white on the underside of its flight feathers.
                   """
    print(find_color(condor_desc))