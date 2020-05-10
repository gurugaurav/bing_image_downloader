
## Bing Image Downloader
######################

Python liberary to download bulk of images form Bing.com.It uses async url, so it is very fast.<br/>


### Disclaimer<br />

This program lets you download tons of images from Bing.
Please do not download or use any image that violates its copyright terms. 

### Installation <br />
```sh
pip install bing-image-downloader
```

or 
```bash
git clone https://github.com/gurugaurav/bing_image_downloader
cd bing_image_downloader
pip install .
```


### Usage <br />
```python
from bing_image_downloader import downloader
downloader.download(query_string, limit=100, adult_filter_off=True, force_replace=False)
```


### PyPi <br />
https://pypi.org/project/bing-image-downloader/
  



