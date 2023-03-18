# austro_bird_classifier
## An End-to-end machine learning project using pytorch, fastai and Flask.

#TLDR
austro_bird_classifier is a CNN-based classifier that can distinguish the 72 most common bird species
found in Austria by image.

You can test it here: **\<add link to Flask app\>**

Just upload a picture of a bird you saw in your garden (given that you live in Austria) and 
it will tell you (most likely) what species that bird belongs to.
Super simple!

# The whole story

## Introduction

My girlfriend is a huge bird nerd. So am I, but she is even more so. I am an ML enthusiast too, so I thought
of a way to combine these, and the idea for the austro_bird_classifier was born.
Though, to be honest, it was not really my idea. I got it from working through the fastai fastbook, where 
you do a very similar thing, just with bears. Anyway, I thought it would be a cool project and that 
was motivation enough.

My goal was, to really do an end-to-end project, i.e. from data to a deployed web app.
I chose to limit myself to the 74 most common birds in Austria (according to Birdlife **\<add birdlife link\>**).
To correctly name 74 different bird species is already not an easy task for us humans (although it is also not that hard,
once you have some experience), so it also should be a little bit of a challenge to train a ML model to do it.
In the following, I will tell you how I went about to do that...

## 1. Data gathering

First, in order to train a ML model on data, you need data. And best would be lots of data.
And where can you get lots of data? Exactly.
In my case, I needed lots of pictures of birds.
There are already some bird picture datasets out there in the internet (e.g. https://www.kaggle.com/datasets/gpiosenka/100-bird-species),
but I don't know of a dataset specifically for austrian birds.
So the next best thing is to just google birds and download the resulting images. Easy, right?
However, a quick back-of-an envelope **(schreibt man so?)** calculation suggests that this is indedd not as easy.
Let's assume that we need at least 50 pictures of each species to allow for a good classification accuracy.
74 * 50 = 3700. Further, assume that it takes around 10 seconds to find a suitable image, click on it and then download it.
3700 * 10 seconds = 37000 seconds ~ 10 hours. And that is the bare minimum. Let's say we want a 100 pictures
per bird species, so double the effort, and you are at 20 hours. Uph **(?)**!
There's gotta be a better way. And actually, there is.

Bing allows you to query pictures via its web API. To use it, you first need a Microsoft Azure account (which is free).
After registration, you can create a Bing Search resource (v7 at the time of writing) which can also be used for free, if you
don't exceed a certain monthly limit of queries to the Bing API.
The lowest-pricing tier includes 1000 queries per month, a maximum of 3 queries per second and up to 150 results per query.
Once you created your resource, you can get a Bing API token from **\< add link where to get token \>**.

To get the maximum out of our free tier, let's do another quick calculation.

We can do 1000 queries with 150 images / query = 150k images.
150k images / 74 species ~ 2027 images / species

To allow some error margin, let's not exceed 2000 images / species.

2000 images / 150 images per queries = 13.333 queries
13.333 is nasty, so let's say 13 queries.

13 queries * 150 images = 1950 images with 13 * 74 = 962 queries.

Even if there are less search results for a species, or some images are unusable, we should
have more than enough training data and still don't pay one cent. Nice.


### Execution

The birds are listed in the data/austrian_birds.csv file. This file will be accessed by all the data gathering scripts.
In there, we have the german name, and the english name of each of the 74 species. The german name, because often times
it is much nicer (e.g. compare Mönchsgrasmücke and black cap) and the english name for the sake of internationality. 

Here and in the following, make sure you execute all the scripts from the same directory. Either cd into
the data directory or run them from the parent directory. It does not matter where, as you long as you do all steps from
the same place. Otherwisem the scripts will not find the necessary files. 

First, to query the Bing API, you need to run

    python query.py <API token>

The query.py will gather all the search results for each species in a separate .csv file. Then run

    python download_urls.py

to actually download the images. You will get one directory for each bird species inside the newly created images
directory.

## 2. Data cleaning

Ok, up until now, everything was easy and nicely automatic. Now, we will have to do some manual labor.
Since we cannot expect that all the search results are what we actually want (which you know if you ever searched
for something on the internet), it is highly important to look at the data and dismiss everything that is not a nice
picture of a bird. We don't want our ML model to train on any of those.

There are two cases:

1) The file cannot be opened at all
2) The file does not depict the desired bird

Luckily for us, the first case can be automated. Unfortunately, the second case cannot.

### Execution

To remove all the images that cannot be opened at all, run

    python remove_faulty_images.py

The script makes use of the PIL.Image class. The assumption is, that if PIL cannot open it, than
the image is corrupt.

For the second case, the only way to really be sure is to go over every image and check if it shows
the bird we were looking for. Bummer.

**TODO: Maybe show some faulty images. Clarify how the legal situation is with showing images from
somewhere on github. If no problem, show Star, show some crap images from other species and refer to
bird dataset on google drive.
If problem, state here that you cannot show the pictures.**

## 3. Train/Test split and mini dataset

So now we have a nice and tidy dataset full of birds. Before we can get our hands dirty with the ML models, there
are still two things to do. First, we need to split all the images into two categories, training and testing.
The ML models will be trained on one dataset and evaluated on the other. But it is also always a good idea, to have
a smaller version of your full dataset, so you can quickly train different ML models and compare their 
performance, without the need to wait the full 3+ hours it takes to train on the full dataset.
Trust me, nothing is more annoying than waiting 3 hours just to find out that nothing changed (or worse, that
the ML model performs worse than before).

### Execution

To split the data, run

    python train_test_split.py

It will create a train and a test child in the images directory.
Then, to create the mini dataset, run 

    python create_mini_ds.py

##3 Training

Ok, so now we have a 
