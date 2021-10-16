import numpy as np
import tensorflow.keras as keras
from src.audio_processing import solve_audio

# The sequence length
kSequenceLength = 128

class HyperTone:
  def __init__(self, model_path_):
    self.model = keras.models.load_model(model_path_)
  
  def predict(self, filepath_, seq_len_=kSequenceLength):
    ret = solve_audio(filepath_)
    x = np.asarray(ret[1])
    x = x[x != 0]

    if len(x) < seq_len_:
      x = padarray(x, seq_len_)
    num_sequences = len(x) - seq_len_ + 1
    seeds = []
    for index in range(num_sequences):
      seeds.append(np.asarray(x[index : index + seq_len_]).reshape((seq_len_, 1)))
    output = self.model.predict(np.asarray(seeds))

    y = []
    for index, elem in enumerate(output):
      y.append(1 + self.sample(elem))
    #a = np.array(y)
    #counts = np.bincount(np.array(y))
    return np.argmax(np.bincount(np.array(y)))
    #return y
    #   # make a prediction
    #   #output = self.model.predict(seed)
    #   output = self.model.predict(seed)[0]
    #   #classes_x=np.argmax(predict_x,axis=1)
    #   #print(f"predict_x={predict_x}")
    #   #print(f"classes_x={classes_x}")
    #   y.append(output)
    #   #print(pr

    #   #print(probabilities)
    #   #index = self.sample(probabilities)
    #   #y.append(1 + index)              
    # return y

  def sample(self, probabilites, temperature=0.1):
    """Samples an index from a probability array reapplying softmax using temperature

    :param predictions (nd.array): Array containing probabilities for each of the possible outputs.
    :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
        A number closer to 1 makes the generation more unpredictable.

    :return index (int): Selected output symbol
    """
    predictions = np.log(probabilites) / temperature
    probabilites = np.exp(predictions) / np.sum(np.exp(predictions))

    choices = range(len(probabilites)) # [0, 1, 2, 3]
    index = np.random.choice(choices, p=probabilites)

    return index