from urllib.parse import ParseResult, urlparse


def convertToHttps(url):
    """ Converts a url to https """
    # https://stackoverflow.com/questions/21659044/how-can-i-prepend-http-to-a-url-if-it-doesnt-begin-with-http
    p = urlparse(url, "https")
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ""

    return ParseResult("https", netloc, path, *p[3:]).geturl()