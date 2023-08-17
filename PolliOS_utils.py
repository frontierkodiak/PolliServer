import cv2
import io
from PIL import Image
import numpy as np

### FUTURE: Import from PolliOS/engine/utils.py


def get_image_from_redis(frame_key, imageDB, output_format='cv2'):
    # Get binary data from Redis
    byte_im = imageDB.get(frame_key)
    if output_format.lower() == 'cv2':
        # Convert binary data to image
        image = Image.open(io.BytesIO(byte_im))
        # Convert PIL image to OpenCV image (numpy array)
        open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return open_cv_image
    elif output_format.lower() == 'jpeg':
        return byte_im
    else:
        print(f'Invalid output format: {output_format}. Please choose from "cv2" or "jpeg".')
        return None
    

def crop_image_absolute_coords(image, bbox_LL_abs, bbox_UR_abs):
    '''
    Crop an image using absolute coordinates.
    '''
    return image.crop((*bbox_LL_abs, *bbox_UR_abs))