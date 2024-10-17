from pathlib import Path
import urllib.request
import urllib
import imghdr
import posixpath
import re
from PIL import Image
from io import BytesIO
import io


'''
Python api to download image form Bing.
Author: Guru Prasad (g.gaurav541@gmail.com)
'''
def image_to_byte_array(image: Image) -> bytes:
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format="PNG")
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr


def resize(url,size: tuple):

    response = urllib.request.urlopen(url)
    img = Image.open(BytesIO(response.read()))
    img=img.resize(size=size,resample=Image.LANCZOS)
    #kl=image_to_byte_array(img)
    # with open('pn.png','wb') as f:
    #     f.write(kl)
    return img

class Bing:
    def __init__(self, query, limit, output_dir, adult, timeout, filter={}, resize=None, verbose=True):
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filter = filter
        self.verbose = verbose
        self.seen = set()


        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout
        assert (type(resize)==tuple) or (resize is None), "resize must be a tuple(height,width)"
        self.resize=resize

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


    def get_filter(self):
        filter_string = ""
        for k, v in self.filter.items():
            k = k.lower()
            filter_string+= eval(f"self.get_{k}(v)")
        return filter_string

    def get_size(self, shorthand):
        if shorthand == "small":
            return "+filterui:imagesize-small"
        elif shorthand == "medium":
            return "+filterui:imagesize-medium"
        elif shorthand == "large":
            return "+filterui:imagesize-large"
        elif shorthand == "extra large":
            return "+filterui:imagesize-wallpaper"
        elif "x" in shorthand:
            w, h = shorthand.split('x')
            return f"+filterui:imagesize-custom_{w}_{h}"
        else:
            return ""

    def get_color(self, shorthand):
        shorthand = shorthand.lower()
        if shorthand in ["color", "color only"]:
            return "+filterui:color2-color"
        elif shorthand in ["grayscale", "black & white"]:
            return "+filterui:color2-bw"
        elif shorthand in ["red", "orange", "yellow", "green", "teal", "blue", "purple", "pink", "brown", "black", "gray", "white"]:
            return f"+filterui:color2-FGcls_{shorthand.upper()}"
        else:
            return ""

    def get_type(self, shorthand):
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

    def get_layout(self, shorthand):
        shorthand = shorthand.lower()
        if shorthand in ["square", "wide", "tall"]:
            return f"+filterui:aspect-{shorthand}"
        else:
            return ""

    def get_people(self, shorthand):
        shorthand = shorthand.lower()
        if shorthand in ["faces", "just faces"]:
            return "+filterui:face-face"
        elif shorthand in ["head&shoulders", "head & shoulders", "portrait"]:
            return "+filterui:face-portrait"
        else:
            return ""

    def get_date(self, shorthand):
        shorthand = shorthand.lower()
        if shorthand in ["day", "past 24 hours"]:
            return "+filterui:age-lt1440"
        elif shorthand in ["week", "past week"]:
            return "+filterui:age-lt10080"
        elif shorthand in ["month", "past month"]:
            return "+filterui:age-lt43200"
        elif shorthand in ["year", "past year"]:
            return "+filterui:age-lt525600"
        else:
            return ""

    def get_license(self, shorthand):
        shorthand = shorthand.lower()
        if shorthand in ["cc", "creative commons", "all creative commons"]:
            return "+filterui:licenseType-Any"
        elif shorthand in ["public", "public domain"]:
            return "+filterui:license-L1"
        elif shorthand in ["share", "free to share and use"]:
            return "+filterui:license-L2_L3_L4_L5_L6_L7"
        elif shorthand in ["modify,share", "free to modify, share, and use"]:
            return "+filterui:license-L2_L3_L5_L6"
        elif shorthand in ["commercial share", "free to share and use commercially"]:
            return "+filterui:license-L2_L3_L4"
        elif shorthand in ["commercial modify,share", "free to modify, share, and use commercially"]:
            return "+filterui:license-L2_L3"
        else:
            return ""

    def save_image(self, link, file_path):
        if not self.resize:

            request = urllib.request.Request(link, None, self.headers)
            image = urllib.request.urlopen(request, timeout=self.timeout).read()
            if not imghdr.what(None, image):
                print('[Error]Invalid image, not saving {}\n'.format(link))
                raise ValueError('Invalid image, not saving {}\n'.format(link))
            with open(str(file_path), 'wb') as f:
                f.write(image)
        elif self.resize:
            request = urllib.request.Request(link, None, self.headers)

            img=resize(request,size=self.resize)
            image=image_to_byte_array(img)
            # if not imghdr.what(None, image):
            #     print('[Error]Invalid image, not saving {}\n'.format(link))
            #     raise ValueError('Invalid image, not saving {}\n'.format(link))
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

            if self.verbose:
                # Download the image
                print("[%] Downloading Image #{} from {}".format(self.download_count, link))

            self.save_image(link, self.output_dir.joinpath("Image_{}.{}".format(
                str(self.download_count), file_type)))
            if self.verbose:
                print("[%] File Downloaded !\n")

        except Exception as e:
            self.download_count -= 1
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))


    def run(self):
        while self.download_count < self.limit:
            if self.verbose:
                print('\n\n[!!]Indexing page: {}\n'.format(self.page_counter + 1))
            # Parse the page source and download pics
            request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
                          + '&first=' + str(self.page_counter) + '&count=' + str(self.limit) \
                          + '&adlt=' + self.adult + '&qft=' + self.get_filter()
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf8')
            if html ==  "":
                print("[%] No more images are available")
                break
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            links = [link.replace(" ", "%20") for link in links]
            if self.verbose:
                print("[%] Indexed {} Images on Page {}.".format(len(links), self.page_counter + 1))
                print("\n===============================================\n")

            for link in links:
                if self.download_count < self.limit and link not in self.seen:
                    self.seen.add(link)
                    self.download_image(link)

            self.page_counter += 1
        print("\n\n[%] Done. Downloaded {} images.".format(self.download_count))
