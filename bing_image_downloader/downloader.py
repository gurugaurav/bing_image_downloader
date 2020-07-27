import os
import shutil

try:
    from bing import Bing
except ImportError:  # Python 3
    from .bing import Bing


def download(query, limit=100, output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=60):

    # engine = 'bing'
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'

    cwd = os.getcwd()
    image_dir = os.path.join(cwd, output_dir, query)

    if force_replace:
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)

    # check directory and create if necessary
    try:
        if not os.path.isdir("{}/{}/".format(cwd, output_dir)):
            os.makedirs("{}/{}/".format(cwd, output_dir))
    except:
        pass
    if not os.path.isdir("{}/{}/{}".format(cwd, output_dir, query)):
        os.makedirs("{}/{}/{}".format(cwd, output_dir, query))

    bing = Bing(query, limit, output_dir, adult, timeout)
    bing.run()


if __name__ == '__main__':
    download('cat', limit=10, timeout='1')
