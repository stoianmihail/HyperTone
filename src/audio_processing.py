import math
import librosa
import numpy as np
from scipy.signal import savgol_filter
import soundfile as sf
import io

# Number of bins per octave (specific for byzatine music)
kBinsPerOctave = 24

# Corresponds to a jump from Pa -> Ga
kJump = int(4/3 * kBinsPerOctave)

fmin = librosa.midi_to_hz(36) # C2 (Ison)
fmax = librosa.midi_to_hz(84) # C6 (highest note ever seen in byzantine sheets: A5#)
print(fmin)
print(fmax)

def find_bin(f):
# Find which bin `f` fits into.
# The bins are geometrically distributed.
# Formula: 2**(i/`kBinsPerOctave`) * fmin
# Source: https://en.wikipedia.org/wiki/Constant-Q_transform
  return int(round(math.log2(f / fmin) * kBinsPerOctave)) if not math.isnan(f) else f

def pad_array(A, size):
  t = size - len(A)
  return np.pad(A, pad_width=(0, t), mode='constant')

def normalize_diffs(bins):
  pitch_diff = []
  last_index_non_nan = None
  for index, elem in enumerate(bins):
    # First position?
    if index == 0:
      continue
    # NaN?
    if math.isnan(elem):
      continue
    # No prev elem which is not NaN?
    if last_index_non_nan is None:
      last_index_non_nan = index
      continue
    diff = bins[index] - bins[last_index_non_nan]

    if abs(diff) > kJump:
      last_index_non_nan = index
      continue

    # isPositive = diff > 0
    # while abs(diff) > kJump and diff < 0:
    #   # `bins[last_index_non_nan]` >= `elem`.
    #   bins[index] += kBinsPerOctave
    #   diff = bins[index] - bins[last_index_non_nan]
      
    # while abs(diff) > kJump and diff > 0:
    #   # `bins[last_index_non_nan]` <= `elem`.
    #   pyin_bins[last_index_non_nan] += kBinsPerOctave
    #   diff = bins[index] - bins[last_index_non_nan]
    
    # Update
    last_index_non_nan = index
    pitch_diff.append(diff)
  return pitch_diff

def solve_audio(obj, file_type_, tone_=0, shouldSkip=False):
  y_, sr_ = librosa.load(obj) if file_type_ == 'file' else sf.read(obj)


  print(y_)
  print(sr_)

  f0_, voiced_flag_, voiced_probs_ = librosa.pyin(y_, fmin=fmin, fmax=fmax)

  # Number of seconds
  num_seconds_ = len(y_) / sr_

  # How many pyin samples / second
  samples_per_second_ = (len(f0_) / num_seconds_)
  
  # Compute the window length
  window_length_ = int(samples_per_second_ / 3)
  if window_length_ % 2 == 0:
    window_length_ += 1

  print(f"num_seconds={num_seconds_}, samples_per_second={samples_per_second_}, window_length={window_length_}")

  # Filter
  num_skips_ = int(samples_per_second_ * 5) if shouldSkip else 0
  print(len(f0_[num_skips_:]))
  yhat_ = savgol_filter(f0_[num_skips_:], window_length_, 1)

  # And determine the bins
  filtered_bins_ = list(map(find_bin, yhat_))
  return [filtered_bins_, normalize_diffs(filtered_bins_), tone_]