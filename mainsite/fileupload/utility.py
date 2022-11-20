# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：   utility
  Description : MiniMES Company
  Author :    Karo Lin
  date：     2022/10/19
  Copyright follow MIT definitions.
-------------------------------------------------
  Change Activity:
          2022/10/19:
-------------------------------------------------
"""
__author__ = 'Karo Lin'

import uuid
import os


# Use uuid as file name.
from io import BytesIO

from PIL import Image, ExifTags
from django.core.files import File


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('icons', filename)


# 壓縮並旋轉Icon檔案，使得方向正確以及避免伺服器空間耗盡。(ImageField use only)
def make_thumbnail(image, file_name, size=(500, 500)):
    """Makes thumbnails of given size from given image"""
    pilImage = Image.open(image)
    w, h = pilImage.size
    print('The original image size is Width:%s, Height:%s.' % (w, h))
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(pilImage._getexif().items())
        if exif[orientation] == 3:
            pilImage = pilImage.rotate(180, expand=True)
        elif exif[orientation] == 6:
            pilImage = pilImage.rotate(270, expand=True)
        elif exif[orientation] == 8:
            pilImage = pilImage.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    pilImage.thumbnail(size)  # resize image
    w, h = pilImage.size
    print('The new image size is Width:%s, Height:%s.' % (w, h))
    if pilImage.mode in ("RGBA", "P"):
        pilImage = pilImage.convert("RGB")  # convert mode
    thumb_io = BytesIO()  # create a BytesIO object
    pilImage.save(thumb_io, 'JPEG', quality=85)  # save image to BytesIO object
    thumbnail = File(thumb_io, name=file_name)  # create a django friendly File object

    return thumbnail

