from pytube import Playlist
from pytube import YouTube
import os

def download_video(url, dir):
  # Author: Alexandru Grigoras
  yt = YouTube(url)
  print("- download video: " + yt.title + " -> " + dir)
  
  video = yt.streams.filter(only_audio=True).first()
    
  # download the file
  out_file = video.download(output_path=dir)
    
  # save the file
  base, ext = os.path.splitext(out_file)
  new_file = base + '.mp3'
  os.rename(out_file, new_file)
    
  # result of success
  print(yt.title + " has been successfully downloaded.")

def download_playlist(url):
  playlist = Playlist(url)
  print('Number of videos in playlist: %s' % len(playlist.video_urls))
  print("download playlist: " + playlist.title)
  
  title = playlist.title.replace(" ", "_")
  if not os.path.exists(title):
    os.mkdir(title)
  for video_url in playlist.video_urls:
    download_video(video_url, title)

playlist_url = 'https://www.youtube.com/playlist?list=PLNa0mpDwqTxLz7HraxnI2Qa4b2CymOQJa'
download_playlist(playlist_url)  
