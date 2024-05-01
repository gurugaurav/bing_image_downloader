from pathlib import Path
import urllib.request
import urllib
import imghdr
import posixpath
import re

'''
Python api to download image form Bing.
Author: Guru Prasad (g.gaurav541@gmail.com)
'''


class Bing:
    def __init__(self, query, limit, output_dir, adult, timeout,  filter='', verbose=True, blacklist=None, file_extension_whitelist=None):
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filter = filter
        self.verbose = verbose
        self.seen = set()
        self.blacklist = blacklist
        self.file_extension_whitelist = file_extension_whitelist
        self.downloaded = []

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

        self.downloaded.append({
            "query": self.query,
            "file_path": file_path,
            "link": link,
        })

    
    def download_image(self, link):
        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_extension = filename.split(".")[-1]
            file_extension = file_extension.lower()
            if file_extension.lower() not in ["jpe", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                file_extension = "jpg"

            if self.file_extension_whitelist is not None and file_extension not in self.file_extension_whitelist:
                return
                
            if self.verbose:
                # Download the image
                print("[%] Downloading Image #{} from {}".format(self.download_count + 1, link))
                
            self.save_image(link, self.output_dir.joinpath("Image_{}.{}".format(
                str(self.download_count + 1), file_extension)))
            self.download_count += 1

            if self.verbose:
                print("[%] File Downloaded !\n")

        except Exception as e:
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    def is_blacklist(self, link):
        if self.blacklist is None:
            return False
        for blacklist_link in self.blacklist:
            if blacklist_link in link:
                return True
        return False

    def run(self):
        while self.download_count < self.limit:
            if self.verbose:
                print('\n\n[!!]Indexing page: {}\n'.format(self.page_counter + 1))
            # Parse the page source and download pics
            request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
                          + '&first=' + str(self.page_counter) + '&count=' + str(self.limit * 2 + 10) \
                          + '&adlt=' + self.adult + '&qft=' + ('' if self.filter is None else self.get_filter(self.filter))
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf8')
            if html ==  "":
                print("[%] No more images are available")
                break
            links_all = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            links_filter = [l for l in links_all if not self.is_blacklist(l)]
            if self.verbose:
                print("[%] Indexed {} Images, {} Filtered Images, on Page {}.".format(len(links_all), len(links_filter), self.page_counter + 1))
                print("\n===============================================\n")

            for link in links_filter:
                if self.download_count < self.limit and link not in self.seen:
                    self.seen.add(link)
                    self.download_image(link)

            self.page_counter += 1
        print("\n\n[%] Done. Downloaded {} images.".format(self.download_count))
