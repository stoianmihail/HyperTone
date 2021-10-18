import os
import time
import flask
import pandas as pd
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
    file = flask.request.files['audio']
    ip = flask.request.environ.get('HTTP_X_REAL_IP', flask.request.remote_addr)

    print(file.filename)
    print(ip)

    if not os.path.exists('recordings'):
      os.mkdir('recordings')
    filepath = os.path.join(app.root_path, 'recordings', f'{ip}-{int(time.time())}-{file.filename}') 
    file.save(filepath)

    prediction = ht.predict(filepath)

    print(prediction)

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