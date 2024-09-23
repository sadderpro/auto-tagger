
"""

TODO: Instead of creating a function to check the status of the access token, add logic to update the access token when it's expired
TODO: modify get_access_token so it handles a request made with no connection to internet

TODO: Create logic to update access using a timestamp instead of a stupid test request

TODO: Test request_album(self) and set_album_info(self, album_response) methods


"""

import requests
import json
import os
import rich
from collections import defaultdict
from rich import print
from rich.console import Console
from rich.text import Text
from time import time

#*----------------------------- STATIC AND GLOBAL VARIABLES -----------------------------


ROOT_SPOTIFY_URL = 'https://api.spotify.com/v1/'
CLIENT_ID = 'ffbd6399354d4907bfd8a82a7d31dfd1'
CLIENT_SECRET = '5e168a7cd54c4b6486d56e8ee2ce3eae'
access_token, token_type, token_timestamp = None, None, None



#*---------------------------- CLASS AND METHOD DECLARATION ------------------------------


class Track:
  def __init__(self, artists, title, number, disc, lyrics='unavailable'):
    self.artists = artists
    self.title = title
    self.number = number
    self.disc = disc
    self.lyrics = lyrics

# I'll work on this later, I promise
#TODO: Add an attribute that contains the number of discs for the album.
class Album:
  

  def __init__(self, identifier):
    self.ID = identifier
    self.tracklist = defaultdict(list)
    print(f'Created new album instance with ID {self.ID}')
    self.request_album()
  





  # TODO: First, let's make sure the album data is retrieved correctly
  def request_album(self):
    # 1. data required for the request
    global access_token, token_type
    link = f'https://api.spotify.com/v1/albums/{self.ID}'

    if access_token is None:
      load_access_token()

    header = {
      'Authorization': f'{token_type} {access_token}', # AUTHORIZATION: Olivia Pierce
    }
    # 2. Making the requests
    response = requests.get(link, headers=header)

    # 3. Handling the request, first make sure the status code is OK
    if response.status_code == 200:
      self.set_album_info(response)
    elif response.status_code == 401:
      print("[WARNING]: Session expired or invalid access token. Generating a new access token, try again")
      get_access_token()
    else:
      #? Not sure whether to code logic to retry a request within the function or outside. This statement will
      #? remain like this for the time being.
      print(f"[ERROR]: Failed to retrieve album data. Status code {response.status_code}. Retry maybe?")









# Helper method to load the tracks to the album instance
# Theoretically works, but it is currently #!UNTESTED
  def set_album_info(self, album_response):
    
    album_response = album_response.json()

    # Set album title and album artist
    self.albumartists = [artist["name"] for artist in album_response["artists"]]
    self.title = album_response["name"]
    self.year = album_response["release_date"][:4]
    self.total_tracks = album_response["total_tracks"]

    # Start adding the tracklist
    for track_item in album_response["tracks"]["items"]:
      artists = [artist["name"] for artist in track_item["artists"]]
      # Append new item to tracklist list (duh)
      track = Track(artists, track_item["name"], track_item["track_number"], track_item["disc_number"])
      self.tracklist[track_item["disc_number"]].append(track)
    print(f"Album info successfully attached to album class with id {self.ID}")








  def print_album_info(self):
    artists = ", ".join(self.albumartists)
    album_info = f"""Album information retrieved:

    Title: {self.title}
    Artists: {artists}
    Year of release: {self.year}

Tracklist:

  """
    print(album_info)
    for disc, tracks in self.tracklist.items():
      print(f"\nDisc {disc}:\n")
      for track in tracks:
        artists = ", ".join(track.artists)
        print(f"{track.number}. {track.title}, Artist(s): {artists}")



#*--------------------------- MODULE/STATIC FUNCTIONS --------------------------


# This seems to work properly :) but it still need to optimize the way it requests token... later

def load_access_token():
  if os.path.exists('access_token.json'):
    with open('access_token.json', 'r') as token_json:
      token_data = token_json.read()
    try:
      token_data = json.loads(token_data)
      # modify global variables according to data retrieved from access_token.json
      global access_token, token_type, token_timestamp
      access_token = token_data["access_token"]
      token_type = token_data["token_type"]
      token_timestamp = token_data["timestamp"]
      print("[green][SUCCESS][/]: access token and token type variables successfully updated")

    # In case the file it loads from is invalid or something  
    except json.decoder.JSONDecodeError:
      print("[ERROR]: access_token.json does not contain valid json data. Creating a new access token...")
      get_access_token()
  else:
    print("[WARNING]: no access token has been found, now requesting a new access token")
    get_access_token()
    




# Seems to work just fine

def get_access_token():
  
  # Constant declarations for this function, #! DO NOT MODIFY
  global access_token, token_type, token_timestamp
  URL = "https://accounts.spotify.com/api/token"
  HEADER = {
    "Content-Type": "application/x-www-form-urlencoded"
  }
  DATA = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
  }

  # First, let's make the request
  response = requests.post(URL, data=DATA, headers=HEADER)
  token_timestamp = time()

  # Honestly I don't know if anything inside this if-statement works, but we'll see
  if response.status_code == 200:
    # save the response in a json file for future use
    response = response.json()
    response["timestamp"] = token_timestamp
#   with open('access_token.json', 'w') as access_token_json:
#     json.dump(response, access_token_json)
#     print("Saved access token as access_token.json")

    # Convert response text (already in json format) to a dictionary
    access_token = response['access_token'] 
    token_type = response['token_type'] 
    print(f'Access token successfully created.')
  #handle error status code  
  else:
    print(f'Failed retrieving data. Status code: {response.status_code}')
    return None

  return response







# ! DEPRECATED !
def get_album(access_token, token_type, album_id):
  header = {
    'Authorization': f'{token_type} {access_token}',
  }

  data = {
    'id': album_id
  }

  response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}', headers=header)
  return response



#uncomment when the module is finished:
#load_access_token()







# ************************** MAIN FUNCTION, FOR TESTING ONLY **************************
# This module is not intended to run as __main__, however, there is a main function to test 
# the functions and class methods within this module. I'm no expert in testing, if you know 
# a more efficient way to test these features, please let me know.


if __name__ == "__main__":

  converting_vegetarians = Album("3LbcBylGvC80f5OTeQaVuM")
  converting_vegetarians.request_album()
  converting_vegetarians.print_album_info()




