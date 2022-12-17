#!/usr/bin/python
"""
download_urls.py

For each species in austrian_birds.csv, download all
images from the urls in the corresponding url file.

Requirements: requests (https://pypi.org/project/requests/)

"""

__author__ = 'Lukas Linauer'
__email__ = 'l.linauer@gmx.at'

import sys
from pathlib import Path
import shutil
import requests


def clean_url_file(url_file):
    """ Remove all urls for which we cannot determine an image type from
        url_file(pathlib.Path object)
    """

    clean_url_list = []

    with open(url_file, 'r') as f:
        url_list = f.readlines()[1:]

    for i, img_url in enumerate(url_list):
        # check the url for the image file type
        if any([img_url.__contains__(end) for end in ['.png', '.PNG', '.jpg', '.jpeg', '.JPG', '.JPEG']]):
            clean_url_list.append(img_url)

    with open(url_file, 'w') as f:
        f.write(f'{str(len(clean_url_list))}\n')
        f.writelines([f'{url}' for url in clean_url_list if url is not None])  # no need for \n, already in file


def read_url_file(url_file):
    """ Read the image urls from url_file(pathlib.Path object).
        The first line consists the max number of urls, that this fail should contain
        After that, every line is the url of an image.
        Return the urls as a list
    """

    with open(url_file, 'r') as f:
        return f.readlines()[1:]


def download_images(url_list, img_path):
    """ For each url in url_list(list), download the corresponding image and save it to img_path(pathlib.Path obj)
        The images will be named with consecutive integers.
        If the download fails, still create a file with the name so that it will not be re-tried the next time.
    """

    # loop over all urls
    for i, img_url in enumerate(url_list):

        # check the url for the image file type
        if '.png' in img_url or '.PNG' in img_url:
            img_type = '.png'
        elif '.jpg' in img_url or '.JPG' in img_url or '.jpeg' in img_url or '.JPEG' in img_url:
            img_type = '.jpg'

        img_file = img_path / f'{i+1}{img_type}'
        if img_file.exists():
            continue

        try:
            res = requests.get(img_url, stream=True)
        except requests.exceptions.TooManyRedirects:
            img_file.touch()
            continue
        except requests.exceptions.SSLError:
            img_file.touch()
            continue
        except requests.exceptions.ConnectionError:
            img_file.touch()
            continue

        if res.status_code != 200:
            print(f'Failed to download image {img_url}')
            img_file.touch()
            continue

        with open(img_file, 'wb') as f:
            shutil.copyfileobj(res.raw, f)


if __name__ == '__main__':

    # read bird species from file
    species_file = 'austrian_birds.csv'
    with open(species_file, 'r') as csv_file:
        species_list = csv_file.readlines()

    url_file_path = Path('urls')
    if not url_file_path.exists():
        print('Path "urls" does not exist. Did you execute query.py?')
        sys.exit()

    img_file_path = Path('images')

    # loop over all species, first line = header
    for species in species_list[1:]:
        name = species.strip('\n').split(',')[0]  # 0 = German, 1 = English
        name = name.replace(' ', '_').lower()  # replace all whitespaces in name with _

        print(f'Species: {name}')
        species_url_file = url_file_path / f'{name}_urls.txt'

        # remove all urls without a known file ending because we don't know what type of image to use
        clean_url_file(species_url_file)

        species_img_path = img_file_path / name
        species_img_path.mkdir(exist_ok=True)

        # loop over each url in species_url_file and download the images
        species_url_list = read_url_file(species_url_file)
        download_images(species_url_list, species_img_path)
