import argparse
import os
import sys

import lyricsgenius


def save_artist_songs(genius, name, max_songs, out_dir):
	"""
	searches on genius.com an artist name and store a max number of songs into a temporary file
	"""
	artist = genius.search_artist(name, max_songs=max_songs, sort="title")
	if artist is not None and artist.songs is not None:
		songs = list(filter(lambda x: x is not None, map(lambda x: x.lyrics, artist.songs)))
		with open(out_dir + name + '.txt', 'w') as f:
			f.write(''.join(songs))
		return len(artist.songs)


def merge_songs(in_dir, output_path):
	"""
	merges all the lyrics divided per artist into a one single file
	"""
	with open(output_path, 'a') as out_file:
		for file in os.listdir(in_dir):
			with open(in_dir + file, 'r') as lyrics_file:
				out_file.write(lyrics_file.read())


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description="this script downloads all songs of a given set of artists and write them on an output file."
	)

	parser.add_argument("-i", "--input",
	                    help="input file containing all the artists you want to search.",
	                    type=str,
	                    default='../data/ingestion/artists.txt')

	parser.add_argument("-o", "--output",
	                    help="output file with all the lyrics found.",
	                    type=str,
	                    default='../data/ingestion/lyrics.txt')

	parser.add_argument("-a", "--access_token",
	                    help="Genius APIs access token to send all your queries.\n"
	                         "Get yours here: https://genius.com/api-clients",
	                    type=str, required=True)

	parser.add_argument("-m", "--max_songs",
	                    help="max number of songs you want to get for each artist",
	                    type=int,
	                    default=None)

	args = parser.parse_args()
	input_path = args.input
	output_path = args.output
	access_token = args.access_token
	max_songs = args.max_songs
	tmp_dir = '.tmp/'

	if os.path.exists(output_path):
		delete_lyrics = input('Lyrics are already present in the given output path. Do you want to proceed? [y/n]')
		if delete_lyrics[0] == 'y' and len(delete_lyrics) == 1:
			os.remove(output_path)
		else:
			print('Exiting ..')
			sys.exit(0)

	if not os.path.isdir(tmp_dir):
		os.makedirs(tmp_dir)

	with open(input_path, 'r') as f:
		artist_names = f.read().splitlines()

	genius = lyricsgenius.Genius(access_token)
	for name in artist_names:
		save_artist_songs(genius, name, max_songs, tmp_dir)

	merge_songs(tmp_dir, output_path)

	os.system('rm -rf ' + tmp_dir)
