import unittest
import sys

sys.path.append('../reggaeton')
from reggaeton.ingestion import *

access_token_path = 'tests/access_token'
tmp_dir = 'tests/tmp/'


class TestIngestion(unittest.TestCase):

	def test_save_artists_songs(self):

		if os.path.exists(access_token_path):
			with open(access_token_path, 'r') as f:
				access_token = f.read()
		else:
			access_token = input('Please paste your Genius access token (next time will be cached):')
			with open(access_token_path, 'w') as f:
				f.write(access_token)

		if not os.path.isdir(tmp_dir):
			os.makedirs(tmp_dir)

		genius = lyricsgenius.Genius(access_token)
		songs_length = save_artist_songs(genius, 'J Balvin', 3, tmp_dir)
		self.assertEqual(songs_length, 3)

	def test_songs_merging(self):
		output_path = 'out.txt'
		merge_songs(tmp_dir, output_path)

		import subprocess
		text1 = subprocess.check_output(f'cat {tmp_dir}*.txt', shell=True)
		text2 = subprocess.check_output(f'cat {output_path}', shell=True)

		self.assertEqual(text1, text2)
		os.system('rm -rf ' + tmp_dir)
		os.system('rm -rf ' + output_path)


if __name__ == '__main__':
	unittest.main()
