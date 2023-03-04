"""
train_test_split.py

Split images into a train and test dataset
"""

import os
import shutil
import random
from pathlib import Path


if __name__ == '__main__':

    img_path = Path('images')

    # loop over all species
    for species in img_path.glob('*'):
        # list everything in the species subfolder
        img_list = os.listdir(species)

        # take random sample, we want a 80-20 split (train-test)
        n_test = int(len(img_list)*0.2)
        test_list = random.sample(img_list, n_test)
        train_list = list(set(img_list) - set(test_list))

        # move the images to the respective folders
        train_path = img_path / 'train' / species.name
        test_path = img_path / 'test' / species.name

        # create directories
        train_path.mkdir(parents=True, exist_ok=True)
        test_path.mkdir(parents=True, exist_ok=True)

        print(f'Splitting {species} into train and test set')
        for img in train_list:
            shutil.move(species / img, train_path / img)
        for img in test_list:
            shutil.move(species / img, test_path / img)

