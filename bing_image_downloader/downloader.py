import os
import shutil

try:
    from bing import Bing
except ImportError:  # Python 3
    from .bing import Bing


def download(query, limit=100, adult_filter_off=True, force_replace=False):

    engine = 'bing'
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'

    cwd = os.getcwd()
    image_dir = os.path.join(cwd, 'dataset', engine, query)

    if force_replace:
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)

    # check directory and create if necessary
    try:
        if not os.path.isdir("{}/dataset/".format(cwd)):
            os.makedirs("{}/dataset/".format(cwd))
    except:
        pass
    if not os.path.isdir("{}/dataset/{}/{}".format(cwd, engine, query)):
        os.makedirs("{}/dataset/{}/{}".format(cwd, engine, query))

    Bing().bing(query, limit, adult)
