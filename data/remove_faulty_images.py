#!/usr/bin/python
"""

remove_faulty_images.py

Loop over all the files in the images directory and remove those that are not
valid images.

Requirements: Pillow (https://pypi.org/project/Pillow/)

"""

__author__ = 'Lukas Linauer'
__email__ = 'l.linauer@gmx.at'


from pathlib import Path
from PIL import Image


def check_image(img_file):
    """ Check the img_file(pathlib.Path object) can be opened with PIL.
        If yes, return True, False otherwise. """

    try:
        Image.open(img_file)
        return True
    except IOError:
        return False


if __name__ == '__main__':

    img_file_path = Path('images')

    # loop over all files
    for f in img_file_path.rglob('*'):

        # only treat .jpg and .png files
        if not any([f.name.__contains__(end) for end in ['.png', '.PNG', '.jpg', '.jpeg', '.JPG', '.JPEG']]):
            continue

        # check if it can be opened. If yes, next. If no, remove.
        if check_image(f):
            continue
        else:
            f.unlink()


