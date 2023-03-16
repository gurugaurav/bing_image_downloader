from pathlib import Path
import urllib.request
import urllib
import imghdr
import posixpath
import re
from time import sleep

'''
Python api to download image form Bing.
Author: Guru Prasad (g.gaurav541@gmail.com)
'''


class Bing:
    def __init__(self, query, limit, output_dir, adult, timeout,  filter='', verbose=True, error_protection=False):
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filter = filter
        self.verbose = verbose
        self.seen = set()
        self.error_protection = error_protection

        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        # self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        self.page_counter = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}


    def get_filter(self, shorthand):
            if shorthand == "line" or shorthand == "linedrawing":
                return "+filterui:photo-linedrawing"
            elif shorthand == "photo":
                return "+filterui:photo-photo"
            elif shorthand == "clipart":
                return "+filterui:photo-clipart"
            elif shorthand == "gif" or shorthand == "animatedgif":
                return "+filterui:photo-animatedgif"
            elif shorthand == "transparent":
                return "+filterui:photo-transparent"
            else:
                return ""


    def save_image(self, link, file_path):
        request = urllib.request.Request(link, None, self.headers)
        image = urllib.request.urlopen(request, timeout=self.timeout).read()
        if not imghdr.what(None, image):
            print('[Error]Invalid image, not saving {}\n'.format(link))
            raise ValueError('Invalid image, not saving {}\n'.format(link))
        with open(str(file_path), 'wb') as f:
            f.write(image)


    def download_image(self, link):
        self.download_count += 1
        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                file_type = "jpg"
            downloaded = False
            if self.verbose:
                # Download the image
                print("[%] Downloading Image #{} from {}".format(self.download_count, link))
            delay = 1
            while self.error_protection:
                try:
                    self.save_image(link, self.output_dir.joinpath("Image_{}.{}".format(
                        str(self.download_count), file_type)))
                    downloaded = True
                    break
                except urllib.error.URLError:
                    if self.verbose:
                        print("[%] URLError, sleeping for " + str(delay))

                    # sleeping for 1 second at a time makes it easier to escape out
                    for i in range(delay):
                        sleep(1)
                    delay *= 2
                    if self.doub_sum(delay) > self.timeout : break

            else:
                self.save_image(link, self.output_dir.joinpath("Image_{}.{}".format(
                    str(self.download_count), file_type)))
                downloaded = True
            if self.verbose and downloaded:
                print("[%] File Downloaded !\n")
            elif self.verbose:
                print("[%] Timeout exceeded : Persistent Connection Error, File not Downloaded !\n")


        except Exception as e:
            self.download_count -= 1
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    # for calculating the error_protection delay
    def doub_sum(self, val):
        sum = 0
        val = int(val)
        while val > 0:
            sum += val
            val //= 2
        return sum

    def run(self):
        while self.download_count < self.limit:
            if self.verbose:
                print('\n\n[!!]Indexing page: {}\n'.format(self.page_counter + 1))
            # Parse the page source and download pics
            request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
                          + '&first=' + str(self.page_counter) + '&count=' + str(self.limit) \
                          + '&adlt=' + self.adult + '&qft=' + ('' if self.filter is None else self.get_filter(self.filter))
            request = urllib.request.Request(request_url, None, headers=self.headers)

            delay = 1
            while self.error_protection:
                try:
                    response = urllib.request.urlopen(request)
                    break
                except urllib.error.URLError:
                    if self.verbose:
                        print("[%] URLError on page, sleeping for " + str(delay))

                    # sleeping for 1 second at a time makes it easier to escape out
                    for i in range(delay):
                        sleep(1.0)
                    delay *= 2
                    if self.verbose:
                        print('\n\n[!!]Retrying page: {}\n'.format(self.page_counter + 1))
                    if self.doub_sum(delay) > max(self.timeout * 4, 30): # pages are very important, so extend the timeout for those
                        break
            else:
                response = urllib.request.urlopen(request)
            if response is not None:
                html = response.read().decode('utf8')
            if html ==  "":
                print("[%] No more images are available")
                break
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            if self.verbose:
                print("[%] Indexed {} Images on Page {}.".format(len(links), self.page_counter + 1))
                print("\n===============================================\n")

            for link in links:
                if self.download_count < self.limit and link not in self.seen:
                    self.seen.add(link)
                    self.download_image(link)

            self.page_counter += 1
        print("\n\n[%] Done. Downloaded {} images.".format(self.download_count))
