import platform
import pathlib
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, send_file
from werkzeug.utils import secure_filename
from fastai.vision.all import *


# make sure, load_learner can read the pickled resnet50 on Linux
if platform.system() == 'Linux':
    pathlib.WindowsPath = pathlib.PosixPath

# setup classifier
model = load_learner('models/bird_classifier_resnet50.pkl')


BIRD_MAP = {
   'Amsel': 'blackbird',
   'Auerhuhn': 'capercaillie',
   'Bachstelze': 'pied wagtail',
   'Baumpieper': 'tree pipit',
   'Bergpieper': 'water pipit',
   'Blaumeise': 'blue tit',
   'Braunkehlchen': 'whinchat',
   'Buchfink': 'chaffinch',
   'Buntspecht': 'great spotted woodpecker',
   'Dohle': 'jackdaw',
   'Eichelhäher': 'jay',
   'Eisvogel': 'kingfisher',
   'Feldlerche': 'skylark',
   'Feldsperling': 'tree sparrow',
   'Fichtenkreuzschnabel': 'red crossbill',
   'Fitis': 'willow warbler',
   'Flussregenpfeifer': 'ringed plover',
   'Flussseeschwalbe': 'common tern',
   'Gartenbaumläufer': 'short-toed treecreeper',
   'Gartengrasmücke': 'garden warbler',
   'Gartenrotschwanz': 'common redstart',
   'Gebirgsstelze': 'grey wagtail',
   'Gelbspötter': 'icterine warbler',
   'Goldammer': 'yellowhammer',
   'Graureiher': 'grey heron',
   'Grauschnäpper': 'spotted flycatcher',
   'Grünfink': 'green finch',
   'Grünspecht': 'green woodpecker',
   'Gänsesäger': 'goosander',
   'Haubentaucher': 'great crested grebe',
   'Hausrotschwanz': 'black redstart',
   'Heckenbraunelle': 'dunnock',
   'Kiebitz': 'northern lapwing',
   'Kleiber': 'nuthatch',
   'Kohlmeise': 'great tit',
   'Kuckuck': 'cuckoo',
   'Lachmöwe': 'black-headed gull',
   'Mauersegler': 'swift',
   'Mehlschwalbe': 'house martin',
   'Misteldrossel': 'mistle thrush',
   'Mäusebussard': 'eurasian buzzard',
   'Mönchsgrasmücke': 'blackcap',
   'Nebelkrähe': 'hooded crow',
   'Neuntöter': 'red-backed shrike',
   'Pirol': 'oriole',
   'Rabenkrähe': 'carrion crow',
   'Rauchschwalbe': 'barn swallow',
   'Rebhuhn': 'partridge',
   'Ringdrossel': 'ring ouzel',
   'Ringeltaube': 'wood pigeon',
   'Rotkehlchen': 'robin',
   'Schwarzstorch': 'black stork',
   'Singdrossel': 'song thrush',
   'Sperber': 'sparrowhawk',
   'Star': 'starling',
   'Stockente': 'mallard',
   'Sumpfmeise': 'marsh tit',
   'Sumpfrohrsänger': 'marsh warbler',
   'Tannenhäher': 'nutcracker',
   'Tannenmeise': 'coal tit',
   'Teichhuhn': 'moorhen',
   'Turmfalke': 'kestrel',
   'Türkentaube': 'collared dove',
   'Uhu': 'eagle owl',
   'Waldbaumläufer': 'eurasian treecrepper',
   'Waldkauz': 'tawny owl',
   'Waldlaubsänger': 'wood warbler',
   'Wasseramsel': 'dipper',
   'Weißstorch': 'white stork',
   'Wintergoldhähnchen': 'goldcrest',
   'Zaunkönig': 'wren',
   'Zilpzalp': 'chiffchaff'
}


# create app
app = Flask(__name__)
app.secret_key = '93324k23f6lgffeer6'
app.config['APPLICATION_ROOT'] = '/birds'


# constants
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


PLOT_NAME = ''


def allowed_file(file_name):
    """ Check if file_name(str) has an allowed extension """
    return '.' in file_name and file_name.split('.')[-1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/', methods=['GET', 'POST'])
def classify_spikes():

    global plot_name

    if request.method != 'POST':
        return render_template('default.html', )
 
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    # if the user does not select a file, the browser submits an empty
    # file without a filename
    if file.filename == '':
        return render_template('default.html', message='No file supplied!')

    if not file:
        return render_template('default.html', message='Invalid file!')

    if not allowed_file(file.filename):
        return render_template('default.html', message='File extension not allowed!')

    # save the file to UPLOAD_FOLDER
    file_name = secure_filename(file.filename)
    file_path = pathlib.Path(UPLOAD_FOLDER) / file_name
    file.save(file_path)

    # classify here
    predicted_bird = model.predict(file_path)[0]

    # translate to english
    english_name = BIRD_MAP[predicted_bird.capitalize()]

    # get URL of file
    img_url = url_for('get_file', filename=file_name)
    return render_template('image_show.html', img_src=img_url, message=f'I think this is a: {predicted_bird.capitalize()} (aka: {english_name})')

