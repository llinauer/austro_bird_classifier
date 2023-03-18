#!/usr/bin/python
"""
query.py

Query the Bing API for birds
Read species from austrian_birds.csv
For each species, get a maximum of 1950 images and save them to
a directory

Requirements: requests (https://pypi.org/project/requests/)

"""

__author__ = 'Lukas Linauer'
__email__ = 'l.linauer@gmx.at'

import sys
from pathlib import Path
import requests

# CONSTANTS
MAX_IMG_PER_SPECIES = 1950
MAX_IMG_PER_CALL = 150


def query_bing(search_term, key, offset=0, min_size=240, max_images=150):
    """ Query the Bing Image search API and search for search_term(str).
        Get only max_images(int, default=150) with minimum size min_size(int, default=120).
        Provide the api_key(str) for the search.
        Skip the first offset(int) images.
        Return the response JSON object as a dictionary
    """

    params = dict(q=search_term, count=max_images, min_height=min_size, min_width=min_size,
                  offset=offset, license='Public')
    search_url = 'https://api.bing.microsoft.com/v7.0/images/search'
    response = requests.get(search_url, headers={"Ocp-Apim-Subscription-Key": key}, params=params)
    response.raise_for_status()
    return response.json()


def check_url_file(url_file):
    """ Check if the url_file(pathlib.Path object) exists.
        If yes, read it and return the current and max number of urls
        If no, return None, None

        The first line consists the max number of urls, that this fail should contain
        After that, every line is the url of an image.
    """

    if not url_file.exists():
        return None, None

    with open(url_file, 'r') as f:
        lines = f.readlines()
        max_num = int(lines[0])
        current = len(lines[1:])
        return max_num, current


def save_urls(url_list, url_file, max_num=None):
    """ Save the urls in url_list(list) to the url_file(pathlib.Path object).
        If the file does not exist, create it and write as a first line the max_num(int, default None)
        If it does exist, append to it.
    """
    if not url_file.exists():
        url_file.touch()

        if max_num is not None:
            with open(url_file, 'w') as f:
                f.write(f'{str(max_num)}\n')

    with open(url_file, 'a') as f:
        f.writelines([f'{url}\n' for url in url_list if url is not None])


if __name__ == '__main__':

    api_key = sys.argv[1] if len(sys.argv) >= 2 else None
    if api_key is None:
        print('Please provide the API key as a command-line argument')
        sys.exit()

    url_file_path = Path('urls')
    url_file_path.mkdir(exist_ok=True)

    # read bird species from file
    species_file = 'austrian_birds.csv'
    with open(species_file, 'r') as csv_file:
        species_list = csv_file.readlines()

    # loop over all species, first line = header
    for species in species_list[1:]:

        name = species.strip('\n').split(',')[0]  # 0 = German, 1 = English
        name = name.replace(' ', '_').lower()  # replace all whitespaces in name with _

        species_url_file = url_file_path / f'{name}_urls.txt'

        # before doing anything, check if the url file already exists
        # this is the case if the execution of the program failed at some point and not all images were loaded
        max_img_urls, current_num = check_url_file(species_url_file)
        next_offset = current_num

        # we want to query a maximum of MAX_IMG_PER_SPECIES images per species.
        # However, it may be possible that there are less than MAX_IMG_PER_SPECIES results for a species
        # To be safe, we look at the estimated number of total results after the first query and
        # adapt the maximum number if necessary

        print(f'Species: {name}')

        # url file does not exist -> first query
        if max_img_urls is None:
            query_result = query_bing(name, api_key, offset=0, max_images=MAX_IMG_PER_CALL)
            est_total = query_result['totalEstimatedMatches']

            # check the estimated total number of results and use it if lower than MAX_IMG_PER_SPECIES
            max_img_urls = min(query_result['totalEstimatedMatches'], MAX_IMG_PER_SPECIES)

            # save the results
            save_urls([d.get('contentUrl', None) for d in query_result['value']], species_url_file, max_img_urls)
            current_num = len(query_result['value'])

            # get the next offset
            next_offset = query_result['nextOffset']

        # if there are already more than max_img_urls - MAX_IMG_PER_CALL urls in the species_url_file -> done
        if current_num > max_img_urls - MAX_IMG_PER_CALL:
            print(f'Total: {current_num}')
            continue

        print(f'{current_num} of {max_img_urls}')

        runs = int((max_img_urls - current_num) / MAX_IMG_PER_CALL)
        remainder = ((max_img_urls - current_num) / MAX_IMG_PER_CALL) - runs

        # do runs queries per species
        for i in range(runs):

            # query bing for images and save urls
            query_result = query_bing(name, api_key, offset=next_offset, max_images=MAX_IMG_PER_CALL)
            save_urls([d.get('contentUrl', None) for d in query_result['value']], species_url_file)
            current_num += len(query_result['value'])

            # get the next offset
            next_offset = query_result['nextOffset']
            print(f'{current_num} of {max_img_urls}')

        # get the remaining images
        remaining_images = int(MAX_IMG_PER_CALL * remainder)

        # query bing for images and save urls
        query_result = query_bing(name, api_key, offset=next_offset, max_images=remaining_images)
        save_urls([d.get('contentUrl', None) for d in query_result['value']], species_url_file)
