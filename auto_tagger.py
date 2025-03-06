import spotify_handler as spotify
from rich import print
import argparse
import music_tag
import subprocess
import os
import re
import csv

# * ------------- USEFUL METHODS ---------------

# helper method to retrieve the album id from a spotify link
def get_id_from_link(album_link):
  
  #first we get the album id from the link using a regular expression
  id_pattern = r"/([^/?]+)\?"
  match = re.search(id_pattern, album_link)
  # then we extract the album id from the link
  return match.group(1) if match else None

# TODO: write logic to 
# Helper method to create a directory with the name of the album
def create_album_dir(album_object):
  # The folder where the new folder will be created.
  music_dir = os.path.join(os.getenv('USERPROFILE'), 'Music')

  # Making the name of the folder and ensuring it only contains valid characters for a windows dir
  dir_name = f'{album_object.albumartists[0]} - {album_object.title}'
  dir_name = re.sub(r'[<>:"/\|?*]', "", dir_name)
  absolute_dir_path = os.path.join(music_dir, dir_name)

  # Creating the folder and returning the path
  if not os.path.exists(absolute_dir_path):
    os.makedirs(absolute_dir_path)
  else:
    print(f"[red]ERROR:[/] The folder {absolute_dir_path} already exists. Check its contents to make sure it doesn't already have an album.")
    return None
  return absolute_dir_path

# This function takes a spotify album link and the path to the tracks to assign the tags
# Note that it does not validate the album object... this will be fixed, in time.
def assign_tags(album_object, tracks_dir=os.getcwd()):
  # list of absolute routes to each track file. Validating it's actually a file and it ends with m4a
  track_files = [os.path.join(tracks_dir, file) for file in os.listdir(tracks_dir) if os.path.isfile(os.path.join(tracks_dir, file)) and os.path.join(tracks_dir, file).endswith('m4a')]
  track_files.sort()
  
  if len(track_files) == album_object.total_tracks:
    count = 0 # counter to manipulate the track_files index in the loop
    for disc_key in album_object.tracklist: # traversing discs
      for track_object in album_object.tracklist[disc_key]: # traversing tracks per disc
        # Applying each corresponding tag to the track
        loaded_track_file = music_tag.load_file(track_files[count])
        loaded_track_file["tracktitle"] = track_object.title
        loaded_track_file["album"] = album_object.title
        loaded_track_file["albumartist"] = "; ".join(album_object.albumartists)
        loaded_track_file["artist"] = "; ".join(track_object.artists)
        loaded_track_file["discnumber"] = track_object.disc
        loaded_track_file["year"] = album_object.year
        loaded_track_file["genre"] = album_object.genres
        loaded_track_file["tracknumber"] = track_object.number
        if album_object.cover_art is not None: loaded_track_file["artwork"] = album_object.cover_art
        # Now we save
        loaded_track_file.save() 
        count += 1 # And move on to the next file
  else:
    print("[red]ERROR:[/] It seems you are not in the right folder. Move to a folder that matches the album or provide a folder path using -p argument")


# * --------------- END OF HELPERS --------------------





# * Argument definitions
parser = argparse.ArgumentParser(description="This program applies tags to a list of files based on a spotify album.")
parser.add_argument("album_arg", help="The Spotify album can be a link or a list of albums saved in a csv file")
parser.add_argument("-p", "--path", default=os.getcwd(), nargs='?')


if __name__ == '__main__':
  
  # * ARGUMENT PARSER
  args = parser.parse_args()


# * INPUT VALIDATION
# the if-elif-else checks for a link, a file path
  if args.album_arg.startswith("https://"):
    album_id = get_id_from_link(args.album_arg)
    # checking if a valid album id could be retrieved from the link. Otherwise, prompt an error message
    if album_id:
      album = spotify.Album(album_id)
      assign_tags(album, args.path)
    else:
      print("[red]ERROR:[/] the link provided is not a valid spotify album url. Please check your input and try again.")
  # TODO: add logic to handle several downloads from a csv file

  # 1. Verify the file exists. Try checking if it's a relative path and compare it to the information provided to the --path argument
  elif os.path.isfile(os.path.join(args.path, args.album_arg)):
    csv_path = os.path.join(args.path, args.album_arg)
    # Open the csv file with DictReader() each row contains a spotify album link and a link to a youtube playlist that corresponds with the album
    # The columns are named spotify and youtube correspondingly.
    missed_albums = []
    with open(csv_path, newline="", encoding="utf-8") as album_list_csv:
      reader = csv.DictReader(album_list_csv)
      
      # Each iteration is an album to download and tag.
      for row in reader:
        # creating the album object to tag and create destination folder for download
        album_id = get_id_from_link(row['spotify'])
        album = spotify.Album(album_id)

        # let's create the destination folder and save it into a variable so yt-dlp can use it later
        album_path = create_album_dir(album)
        
        # now we call yt-dlp to download whatever it is we need to download using subprocess.run
        yt_dlp_args = ["yt-dlp", "-P", album_path, row['youtube']]

        try:
          subprocess.run(yt_dlp_args, check=True)
          assign_tags(album, album_path)
        except subprocess.CalledProcessError as e:
          # In case any errors occur during execution of yt-dlp. Ezpz
          print(f"[red]ERROR:[/] error al descargar el album {album.title} de {album.albumartists[0]}. El error ocurrió al ejecutar yt-dlp")
          missed_albums.append({'spotify': row["spotify"], 'youtube': row["youtube"]})
      # this creates the csv file with the albums yt-dlp was unable to download, if any.
      if len(missed_albums) > 0:
        with open('missed.csv', 'w') as missed_csv:
          fieldnames = ['spotify', 'youtube']
          writer = csv.DictWriter(missed_csv, fieldnames=fieldnames)
          writer.writeheader()
          writer.writerows(missed_albums)



  else:
    print("[red]ERROR:[/] please enter a valid argument. It can either be a link to a spotify album or a path to a csv file with a list of album links.")

