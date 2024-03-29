# austro_bird_classifier
## An End-to-end machine learning project using pytorch, fastai and Flask

# TLDR

austro_bird_classifier is a CNN-based classifier that can distinguish the 72 most common bird species
found in Austria by image.

You can test it here: https://austro-bird-classifier.azurewebsites.net/ (currently not active)

Just upload a picture of a bird you saw in your garden (given that you live in Austria), and 
it will tell you (most likely) what species that bird belongs to.
Super simple!

<p>
     <img src=https://user-images.githubusercontent.com/85884720/228293840-5f5589fe-b829-433b-a957-a79a124fe390.png width=600>
</p>



# The whole story

## Introduction

My girlfriend is a huge bird nerd. So am I, but she even more so. I am an ML enthusiast too, so I thought
of a way to combine these, and the idea for the austro_bird_classifier was born.
Though, to be honest, it was not really my idea. I got it from working through the fastai [fastbook](https://github.com/fastai/fastbook), where 
you do a very similar thing, just with bears. Anyway, I thought it would be a cool project and that 
was motivation enough.

My goal was, to really do an end-to-end project, i.e. from data to a deployed web app.
I chose to limit myself to the 74 most common birds (72 in the end) in Austria (according to [Birdlife](https://birdlife.at/page/vogelbestimmung)).
To correctly name that many different bird species is already not an easy task for us humans (although it is also not that hard,
once you have some experience), so it also should be a little bit of a challenge to train a ML model to do it.

This repository is meant to be more of a blog post, than a working code repo.
Of course the code in here works, and you can also re-create the whole project if you like (see section [DIY](https://github.com/llinauer/austro_bird_classifier/blob/main/README.md#diy))
but, the main focus is on what was done, not how it was done.
So, the code is split up into several .py files and jupyter notebooks, and there is no nice user interface.
That being said, let me tell you how this project came to be.

## 1. Data gathering

First, in order to train a ML model on data, you need data. And best would be lots of data.
And where can you get lots of data? Exactly.
In my case, I needed lots of pictures of birds.
There are already some bird picture datasets out there in the internet (e.g. https://www.kaggle.com/datasets/gpiosenka/100-bird-species),
but I don't know of a dataset specifically for austrian birds.
So the next best thing is to just google birds and download the resulting images. Easy, right?
However, a quick back-of-the envelope calculation suggests that this is indeed not that easy.
Let's assume that we need at least 50 pictures of each species to allow for a good classification accuracy.
74 * 50 = 3700. Further, assume that it takes around 10 seconds to find a suitable image, click on it and then download it.
3700 * 10 seconds = 37000 seconds ~ 10 hours. And that is the bare minimum. Let's say we want a 100 pictures
per bird species, so double the effort, and you are at 20 hours. Oh dear.
There's gotta be a better way. And actually, there is.

Bing allows you to query pictures via its web API. To use it, you first need a Microsoft Azure account (which is free).
After registration, you can create a Bing Search resource (v7 at the time of writing) which can also be used for free, if you
don't exceed a certain monthly limit of queries.
The lowest-pricing tier includes 1000 queries per month, a maximum of 3 queries per second and up to 150 results per query.
Once you created your resource, you can get a token which you can use to authenticate against the API.

To get the maximum out of our free tier, we need to utilize a little bit more maths:


We can do 1000 queries with 150 images / query = 150k images.
150k images / 74 species ~ 2027 images / species

To allow some error margin, let's not exceed 2000 images / species.

2000 images / 150 images per queries = 13.333 queries
13.333 is nasty, so let's say 13 queries.

13 queries * 150 images = 1950 images with 13 * 74 = 962 queries.

Even if there are less search results for a species, or some images are unusable, we should
have more than enough training data and still don't pay one cent. Nice.

As a short legal notice, to be safe, I am only using images that are free to share and use for personal purposes.


## 2. Data cleaning

Ok, up until now, everything was easy and nicely automatic. Now, we will have to do some manual labor.
Since we cannot expect that all the search results are what we actually want (which you know if you ever searched
for something on the internet), it is highly important to look at the data and dismiss everything that is not a nice
picture of a bird. We don't want our ML model to train on any of those.

There are two cases:

1) The file is not an image at all
2) The image does not depict the desired bird

Luckily for us, the first case can be automated. Unfortunately, the second case cannot.
Ok, so by utilizing the PIL.Image class, we can quickly remove all images of the first case.
Then, the fun part begins. Going over every one of the bird species and looking at every image truly is 
a pain in the ass. However, quickly, it becomes obvious why this is important.
For example, the Buchfink:


<p float="left">
     <img src=https://user-images.githubusercontent.com/85884720/228279357-a1cee08d-064c-46ce-a91b-c43efaca5070.jpg width=200>
     &nbsp; &nbsp; 
     <img src=https://user-images.githubusercontent.com/85884720/228280122-90be8e9d-9743-4ef0-928b-4de6a7f26f5a.jpg width=200>
     &nbsp; &nbsp; 
     <img src=https://user-images.githubusercontent.com/85884720/228279390-e43bbf9d-d468-4398-9b1b-91ea111b443c.jpg width=200>
</p>

The first picture shows some eggs, which may be from a Buchfink but that's not what we wanted. The second shows a drawn Buchfink and that's also not what
we wanted. And the last obviously is a Spatz, so nice try.
As you see, data cleaning really is important. The case of the Spatz is actually crucial. In order to train an ML model to distinguish different classes, you actually need data that correctly displays these classes. And in order to get his, you (or somebody else) actually needs to know what constitutes correct data. That's why domain knowledge is so important in Machine Learning.

A curious case is that of the Star (starling). When searching for Star, you will get e.g. 

<p float="left">
     <img src=https://user-images.githubusercontent.com/85884720/228281774-b847d578-5051-4442-beca-5d12a42e4ef7.gif width=200>
</p>

This is, well, a star. Here, there is actually nothing wrong with the search result, but with the query itself. The german name tricked us.
So let's use the english name for the Star. All good.
After this painstakingly long process, we are left with 13473 images. That's pretty impressive! 
Unfortunately, there were not enough good pictures for the Reiherente and the Wachtel, so they did not make
it into the final dataset. May they be forever in our hearts.


## 3. Train/Test split and mini dataset

Now  we have a nice and tidy dataset full of birds. Before we can get our hands dirty with the ML models, there
are still two things to do. First, we need to split all the images into two categories, training and testing.
The ML models will be trained on one dataset and evaluated on the other. But it is also always a good idea, to have
a smaller version of your full dataset, so you can quickly train different ML models and compare their 
performance, without the need to wait the full 3+ hours it takes to train on the full dataset.
Trust me, nothing is more annoying than waiting 3 hours just to find out that nothing changed (or worse, that
the ML model performs worse than before).
For splitting, let's use 80% of the images (10677) for training and 20% (2769) for testing.
The mini dataset should contain only so many images, so that you can quickly train a ML model and 
get a good estimate of its performance. That's pretty vague, I know. 
To be more specific, a good idea is to have a number of x * maximum batch size of your GPU, with 
x around 4 or 5. Then you can sweep through the whole dataset in 4 or 5 batches, and you still get a good
estimate of performance. The same goes for the mini test data set.
Since I am using a batch size of 256, I tailored my mini dataset to consist of 1024 training images and 
512 test images. 


## 4. Training

Alright, with that we can begin the training process. Until now, I always vaguely spoke of ML models, but which
model should we actually use? There are numerous possible answers to this questions, but a good choice for an amateur project like this
is any kind of Convolutional Neural Network (CNN). And one kind of CNN achieves very impressive results on image classification
tasks, while still being small enough to be trained quickly. The ResNet.
ResNet is short for Residual Neural Network. In short, ResNets learn "the residual functions with respect to the layer input,
instead of learning unreferenced functions". Sounds complicated, and it kinda is, so don't worry too much about
the details. If you are interested, you can read the [ResNet paper](https://arxiv.org/pdf/1512.03385.pdf).
The main benefit of this "learning of residuals" is, that it allows for the training of much deeper networks
than otherwise possible. And deeper networks lead to an increased performance in classification (in reality, it is not as straightforward as that,
but, it's a good approximation).
Ok, so a ResNet it is. But which one? Meaning, how deep should the network actually be?
This is a good question, and the answer is: it kinda depends on your data.
So, different network sizes will behave differently for different kinds of data. The only real way to find out, is by trying.
And that is what our mini dataset is for. 

But first, a quick word on software. I mainly used the [fastai library](https://www.fast.ai/) for training here,
because it allows to quickly build and train a good performing model by providing a baseline framework
for many tasks. However, it also has numerous drawbacks (e.g. poor documentation, too much reliance on Jupyter Notebooks, etc.)
and prefer using pytorch (on which it is based) most of the time. But, as said, for quickly getting good results (which was
my focus in this project) it works pretty neat.

One thing that fastai provides you, is pre-trained models. For image classification, we actually don't need (and want) to
train our network from scratch. There are numerous image classification datasets and models that were trained on them out there.
By using a method called transfer learning, we can take such a pre-trained model, adapt it to our own dataset and can 
get impressive results, even with rather small datasets.

Ok, so back to the model discussion. We want to build on a pre-trained ResNet.
I chose to take a closer look at four different models. The ResNet34, XResNet34, ResNet50 and XResNet50.
The 34 and 50 means the number of residual layers in the network. The XResNets utilize some additional hacks
from the ['Bag of Tricks' paper](https://arxiv.org/pdf/1812.01187.pdf).
I trained those four models on the mini training data set (15 epochs each) and evaluated their performance in terms
of accuracy on the mini test data set. Additionally, I used data augmentation (resizing, normalization) and [mixed
precision training](https://arxiv.org/pdf/1710.03740.pdf).

The results are as follows:

| **Model** | **Accuracy** |
|-----------|--------------|
| Resnet34  |     9.6%     |
| XResnet34 |     9.2%     |
| Resnet50  |     76%      |
| XResnet50 |     8.8%     |

Whoa, now that's a clear answer. Tbh, I am not really sure, why the Resnet50 outperforms the others
by such a large margin on the mini data set. It may be due to the composition of the data set, my data augmentation
techniques or other factors. But, for this application, I don't really care. As long as I get a good accuracy, I am happy.

With that information, let's go back to the full data set and train the Resnet50 for, say, 50 epochs.
Luckily, I have a Nvidia Geforce RTX A5500 at my disposal, so training only takes about 3(!) hours.
Awesome. After 50 epochs, we get a whooping 92.2% accuracy on the test data set.
What we could do now, is go back and combine the training and test data set into one big pile, train again
and profit from the additional training examples. I am not going to that here, though, I am satisfied with the 92%.


## 5. Deployment

The last ingredient, is to package everything into a nice (depends, on who you ask) web app and deploy it for everybody to use.
Since I now already have an Azure account, I am going to do that on Azure. There are plenty of other platforms 
where you can deploy python apps easily, but most of them won't be free anyway (depending on the size of the app), so I figured, might as well.
For my web app, I am going to use [Flask](https://flask.palletsprojects.com/en/2.2.x/). Flask is super simple to learn, and it allows you to quickly
build (really horribly looking) web apps. Beauty is in the eye of the beholder anyway, so I spare myself the hassle
of trying to get a fancy CSS styling to work (which it won't anyway) and just stick to bare-bone HTML.

A quick test, shows that I can access my web app locally, and it does what it should.

<p float="left">
     <img src=https://user-images.githubusercontent.com/85884720/228289147-14512e14-ca06-4eda-916e-8f3a821e44ed.png width=200>
</p>

Cool, this clearly is an Auerhuhn!

The deployment is actually as easy. If you are using VS Code, you can just install the Azure extension there,
login to Azure, create a new App Service Plan and start deploying. Stunning.
Unfortunately, since our App is quite bulky (pytorch alone needs around 900 MB of disk space), the Free tier
is no option here. I needed to increase to the B2 tier, which costs around 3 cents / hour. Ouch!
After some waiting time, the app is deployed and ready to be accessed at:

https://austro-bird-classifier.azurewebsites.net/ (currently not active)

Another test, another success!

<p float="left">
     <img src=https://user-images.githubusercontent.com/85884720/228289621-d4522041-a082-44c6-996e-c96576e7fddb.png width=200>
</p>

Now, what happens, if I were to supply a different image, one that does not show a bird?
Hmm, let's test. How about I upload a picture of me?

<p float="left">
     <img src=https://user-images.githubusercontent.com/85884720/228290848-41bdeb6b-abc1-435b-bc52-7833ceb581a1.png width=200>
</p>

Well, not quite. I still feel flattered, though.

Thank you for reading! I hope you enjoyed it!


# DIY

In this section, I will briefly show you how you can re-create the whole project.
Basically, there are three directories: data, training and web.
The data directory contains all scripts needed to re-create the dataset, the training directory contains 
jupyter notebooks needed for training the ML model, and the web directory contains the necessary code for
deploying the Flask app.

## Data

In order to re-create the data set, you first need to create an Azure account and a Bing search resource.
With the corresponding token, you can then run

    python query.py <API token>

Legally, to be on the safe side, you can specify the license of the images to be searched.
I used 'Public', here which grants the users the most rights possible (with possbily 

The query.py will gather all the search results for each species in a separate .csv file. Then run

    python download_urls.py

to actually download the images. You will get one directory for each bird species inside the newly created images
directory.

To remove all the images that cannot be opened at all, run

    python remove_faulty_images.py

Then you will have to go over every image and check if correctly depicts the mentioned bird
(sorry, there is just no way around that).

Once, you have a fine-and-dandy looking dataset, run

    python train_test_split.py

to split into a training and a test dataset.


## Training

For training, you can use the training.ipynb jupyter notebook. It works as is (just to be sure to install the necessary 
python packages).
In there, I am using the Resnet50 architecture. Of course, you can also experiment with other
architectures if you like. Just exchange the architecture in the notebook and tune the hyper-parameters.
Maybe you can even achieve better results!

## Web

To deploy the web app, you can utilize the existing code in the web directory. 
Since the model itself is too big for the github repo, you will have to add it to the models directory
in web. Then, change the name of the loaded model in app.py
You will need to install some additional python packages to run the app.
There is a requirements.txt file provided in the web directory, so you can just run

    pip install -r requirements.txt
    
there

To test the Flask app locally, run

    export FLASK_APP=<name_of_your_app.py>
    python -m flask run

It will start the app on your localhost at port 5000. Go to localhost:5000 in your browser, and you should see the app.
