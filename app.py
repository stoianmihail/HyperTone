import flask
import pickle
import pandas as pd
from src.predict import HyperTone

ht = HyperTone(f'model/model-1634386470.hdf5')

# Initialise the Flask app
app = flask.Flask(__name__, template_folder='templates', static_folder='static')

# Set up the main route
@app.route('/', methods=['GET', 'POST'])
def main():
  if flask.request.method == 'GET':
    print(flask.request)
    # Just render the initial form, to get input
    return(flask.render_template('index.html'))

  if flask.request.method == 'POST':
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