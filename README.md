# austro_bird_classifier
## An End-to-end machine learning project.

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
In the following, I will tell you how I went about to do that:

## 1. Data gathering

First, in order to train a ML model on data, you need data. And best would be lots of data.
And where can you get lots of data? Exactly.
In my case, I needed lots of pictures of birds. So just google birds and download the results. Easy, right?
However, a quick back-of-an envelope **(schreibt man so?)** calculation suggests that this is indedd not as easy.
Let's assume that we need at least 50 pictures of each species to allow for a good classification accuracy.
72 * 50 = 3600. Further, assume that it takes around 10 seconds to find a suitable image, click on it and then download it.
3600 * 10 seconds = 36000 seconds = 10 hours. And that is the bare minimum. Let's say we want a 100 pictures
per bird species, so double the effort, and you are at 20 hours. Uph **(?)**!
There's gotta be a better way. And actually, there is.

Bing allows you to query pictures via it's web API.

