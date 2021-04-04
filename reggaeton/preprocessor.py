import argparse
import unicodedata
import re
import os
import numpy as np
import dill
from polyglot.detect import Detector
from constants import WINDOW_SIZE, MIN_WORD_FREQUENCY
from tensorflow.keras.preprocessing.text import Tokenizer


class Preprocessor:
    def __init__(self):
        self.text = ''
        self.strophes = []
        self.words = {}
        self.ignored_words = {}
        self.tokenizer = None
        self.total_words = 0
        self.x = []
        self.y = []

    def read_normalized_data(self, input_path):
        """
        read lyrics data and convert characters to a well known standard
        """
        with open(input_path, 'r') as file:
            text = file.read().lower()
        self.text = unicodedata.normalize("NFC", text)

    def remove_unwanted_chars(self):
        """
        remove unwanted chars from lyrics
        """
        self.text = re.sub(r"\[.*?\]", '', self.text)
        self.text = re.sub(r"\(.*?\)", '', self.text)
        self.text = re.sub(r"[\d!¡¿?\[\]\(\)\"\*\.#$%&\+\-/;—<=>@^_`'\|{}~“”’:,]", '', self.text)
        self.text = re.sub(r'\n\n+', '\n\n', self.text)

    def split_strophes(self):
        """
        split text into strophes
        """
        self.strophes = self.text.split('\n\n')

    def filter_by_language(self):
        """
        filters only spanish strophes
        """
        def is_spanish(block):
            try:
                res = Detector(block, quiet=True)
                return res.language.code == 'es'
            except:
                pass

        self.strophes = list(filter(is_spanish, self.strophes))

    def filter_weak_data(self):
        """
        filters out strophes shorter than the window size
        """
        def is_greater_than_window_size(block):
            words = block.split(' ')
            return len(words) >= WINDOW_SIZE

        self.strophes = list(filter(is_greater_than_window_size, self.strophes))

    def strophes_in_words(self):
        """
        split strophes into words
        """
        def clean_form(block):
            block = block.replace('\n', ' \n ')
            block = block.split(' ')
            return [x for x in block if x.strip() != '' or x == '\n']

        self.strophes = list(map(clean_form, self.strophes))

    def find_total_and_ignored_words(self, min_word_frequency):
        """
        store all words found in lyrics
        also store as 'ignored' all the words which appear less than min_word_frequency times
        """
        word_freq = {}

        for strophe in self.strophes:
            for word in strophe:
                word_freq[word] = word_freq.get(word, 0) + 1

        self.ignored_words = {k for k, v in word_freq.items() if v < min_word_frequency}
        self.words = word_freq.keys() - self.ignored_words
        self.total_words = len(self.words) + 1

    def generate_tokenizer(self):
        """
        feed a tokenizer using all the valid words found in the lyrics
        """
        self.tokenizer = Tokenizer(filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t')
        self.tokenizer.fit_on_texts(self.words)

    def _is_valid(self, sequence):
        """
        a sequence is valid if every word that contains is not in the ignored set
        """
        for word in sequence:
            if word in self.ignored_words:
                return False
        return True

    def generate_training_and_test_set(self, window_size):
        """
        split training and test set
        """
        for strophe in self.strophes:
            for i in range(0, len(strophe) - window_size):
                sentence = strophe[i: i + window_size + 1]
                if self._is_valid(sentence):
                    self.x.append(sentence[:-1])
                    self.y.append(sentence[-1])

    def shuffle_sequences(self):
        """
        shuffles training and test set
        """
        tmp_x = []
        tmp_y = []

        for i in np.random.permutation(len(self.x)):
            tmp_x.append(self.x[i])
            tmp_y.append(self.y[i])

        self.x, self.y = tmp_x, tmp_y

    def serialize_preprocessor(self, output_path):
        """
        stores a serialized copy of the preprocessor object
        """
        with open(output_path, 'wb') as handle:
            dill.dump(self, handle)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="this script cleans the dataset. The output will be ready-to-go for training."
    )

    parser.add_argument("-i", "--input_path",
                        help="input file containing lyrics previously downloaded.",
                        type=str,
                        default='../data/ingestion/lyrics.txt')

    parser.add_argument("-o", "--output_path",
                        help="output file will be a serialized Preprocessor object",
                        type=str,
                        default='../data/preprocessing/preprocessor.dump')

    parser.add_argument("-s", "--spanish_only",
                        help="tells to the script to keep or not only spanish lyrics.",
                        type=bool,
                        default=True)

    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    spanish_only = args.spanish_only

    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    pr = Preprocessor()

    pr.read_normalized_data(input_path)
    pr.remove_unwanted_chars()

    pr.split_strophes()

    if spanish_only:
        pr.filter_by_language()

    pr.filter_weak_data()
    pr.strophes_in_words()

    pr.find_total_and_ignored_words(MIN_WORD_FREQUENCY)
    pr.generate_tokenizer()

    pr.generate_training_and_test_set(WINDOW_SIZE)
    pr.shuffle_sequences()

    pr.serialize_preprocessor(output_path)
