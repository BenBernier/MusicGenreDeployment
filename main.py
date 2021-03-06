from flask import Flask, render_template, request, send_from_directory
from wtforms import Form, TextAreaField, validators
from tensorflow.keras.models import load_model
import librosa 
import numpy as np
import os
import io
#from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'tmp'
#use this for windows
#UPLOAD_FOLDER = 'static'
app = Flask(__name__)
MYDIR = os.path.dirname(__file__)
#bucket_name = 'musicgenrebucket'

#client = storage.Client.from_service_account_json('./creds/flask-testing-346413-f118304b860e.json')
#bucket = client.get_bucket(bucket_name)


model = load_model('./music_model/model.h5')
classes = {0:'blues', 1:'classical', 2:'country', 3:'disco', 4:'hiphop',
                5:'jazz', 6:'metal', 7:'pop', 8:'reggae', 9:'rock'}   
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

###Classifier
def classify(song):
    #down_blob = bucket.blob(song)
    #file_string = down_blob.download_as_string()
    #audio, sample_rate = librosa.load(io.BytesIO(file_string), res_type='kaiser_fast')
    song_url = os.path.join(MYDIR, "tmp/", song)
    print("PATH: " + song_url)
    #print("This is the file in classify: " + song.filename)
    #print("This is the new absolute path: " + song_url)
    #with io.open(os.path.join(MYDIR, app.config['UPLOAD_FOLDER'], song), 'rb') as song_file:
    audio, sample_rate = librosa.load(song_url, res_type='kaiser_fast') 
    mfccs_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    mfccs_scaled_features = np.mean(mfccs_features.T,axis=0)
    mfccs_scaled_features=mfccs_scaled_features.reshape(1,-1)
    predicted_value=model.predict(mfccs_scaled_features)
    predicted_label=np.argmax(predicted_value,axis=1)
    prediction_genre = classes[predicted_label[0]]
    print("GENRE: " + prediction_genre)
    return prediction_genre

###Flask

ALLOWED_EXTENSIONS = set(['wav'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SongChoice(Form):
    musicsong = TextAreaField('', [validators.DataRequired(), validators.length(min=5)])
    pass
    

@app.route("/")
def home():
    form = SongChoice(request.form)
    return render_template("project.html", form=form)
    
@app.route('/results', methods=['POST'])
def results():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        #filename = secure_filename(file.filename)
        file.save(os.path.join(MYDIR, app.config['UPLOAD_FOLDER'], filename))
        #filepath = os.path.join(MYDIR, app.config['UPLOAD_FOLDER'], filename)
        #upload_blob = bucket.blob("0"+filename)
        #upload_blob.upload_from_filename(os.path.join(MYDIR, app.config['UPLOAD_FOLDER'], filename))
        #print(filepath)
        #file.save(filepath)
        #print(file.path)
        y = classify(filename)
        #y = "test text for debugging"
       
        return render_template('results.html',
                                content=filename,
                                song=filename,
                                prediction=y)
    #return render_template('project.html', form=form)
    
@app.route('/music', methods=['GET', 'POST'])
def music():
    if request.method == 'POST':
        audio_file_name = request.form['text']
        print(audio_file_name)
        return render_template('music.html',
                                song=audio_file_name)
    
if __name__ == "__main__":
    app.run(debug=True)