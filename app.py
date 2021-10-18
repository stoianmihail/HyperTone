import os
import time
import json
import flask
import pandas as pd
import firebase_admin
from firebase_admin import db, credentials, storage
from pydub import AudioSegment

# Init firebase.
cred = None
if 'DYNO' in os.environ:
  print(os.environ.get('GOOGLE_CREDENTIALS'))
  json_data = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
  print(json_data)
  json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
  cred = credentials.Certificate(json_data)
else:
  cred = credentials.Certificate('private-key.json')
  firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://hyper-tone-default-rtdb.firebaseio.com',
    'storageBucket': 'hyper-tone.appspot.com',
  })

from src.predict import HyperTone
ht = HyperTone(f'model/model-1634386470.hdf5')

# Initialise the Flask app
app = flask.Flask(__name__, template_folder='templates', static_folder='static')

# The app must use https for recording to work!
# Only trigger SSLify if the app is running on Heroku,
# acc. https://stackoverflow.com/questions/15116312/redirect-http-to-https-on-flaskheroku/22137608.
from flask_sslify import SSLify
if 'DYNO' in os.environ:
  sslify = SSLify(app)

@app.route('/record', methods=['GET', 'POST'])
def record():
  print(f"request={flask.request.method}")
  if flask.request.method == 'GET':
    print("GET!")
    return {'success' : True}
  if flask.request.method == 'POST':
    # Fetch the file.
    file = flask.request.files['audio']
    
    # Fetch the IP.
    ip = flask.request.environ.get('HTTP_X_REAL_IP', flask.request.remote_addr)

    # Create a directory if we don't have one.
    if not os.path.exists('recordings'):
      os.mkdir('recordings')

    # Build the filepath.
    filename = f'{ip}-{int(time.time())}-{file.filename}'
    wavFilepath = os.path.join(app.root_path, 'recordings', f'{filename}.wav')
    mp3Filepath = os.path.join(app.root_path, 'recordings', f'{filename}.mp3')
    file.save(wavFilepath)

    # Convert to mp3.
    AudioSegment.from_wav(wavFilepath).export(mp3Filepath, format='mp3')

    # Predict the tone.
    prediction = ht.predict(mp3Filepath, 'file')
    print(prediction)
    
    # TODO: add into DB.
    # Store the recording.
    storage.bucket().blob(f'recordings/{filename}.mp3').upload_from_filename(mp3Filepath);

    # And return the result.
    # TODO: return the db key.
    return {'tone' : int(prediction), 'success' : True}

# Set up the main route
@app.route('/', methods=['GET', 'POST'])
def main():
  print(f"Inside: {flask.request.method}")
  if flask.request.method == 'GET':
    print(flask.request)
    # Just render the initial form, to get input
    return(flask.render_template('index.html'))

  if flask.request.method == 'POST':

    print(flask.request.form['audio'])

    # Extract the input
    temperature = flask.request.form['temperature']
    humidity = flask.request.form['humidity']
    windspeed = flask.request.form['windspeed']

    # Make DataFrame for model
    input_variables = pd.DataFrame([[temperature, humidity, windspeed]],
                                    columns=['temperature', 'humidity', 'windspeed'],
                                    dtype=float,
                                    index=['input'])

    # Get the model's prediction
    prediction = ht.predict('samples/Ceea-ce-esti-mai-cinstita_1.m4a')
    #model.predict(input_variables)[0]

    # Render the form again, but add in the prediction and remind user
    # of the values they input before
    return flask.render_template('index.html',
                                  original_input={'Temperature':temperature,
                                                  'Humidity':humidity,
                                                  'Windspeed':windspeed},
                                  result=prediction,
                                  )

if __name__ == '__main__':
  app.run()