from PIL import Image
import urllib.request
from io import BytesIO
import io

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