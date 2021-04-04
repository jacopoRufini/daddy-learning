import unittest

import sys

sys.path.append('../reggaeton')
from reggaeton.preprocessor import *


class TestPreprocessor(unittest.TestCase):

    def setUp(self):
        self.p = Preprocessor()

    def test_read_normalized_data(self):
        input_path = '../data/ingestion/lyrics.txt'
        self.p.read_normalized_data(input_path)
        self.assertTrue(self.p.text.islower())
        self.assertTrue(unicodedata.is_normalized('NFC', self.p.text))

    def test_remove_unwanted_chars(self):
        self.p.text = '[This is gonna be removed](This too)\n\n\nText\n\n\n1234567890!¡¿?[]()"*.#$%&+-/;—<=>@^_`|{}~“”’:,'
        self.p.remove_unwanted_chars()
        self.assertEqual(self.p.text, '\n\nText\n\n')

    def test_split_strophes(self):
        self.p.text = '\n\nThis is a\n\ntext\n\n'
        self.p.split_strophes()
        self.assertTrue(len(self.p.strophes), 3)

    def test_filter_by_language(self):
        english_text = 'Amy normally hated Monday mornings, but this year was different. Kamal was in her art class and she liked Kamal. She was waiting outside the classroom when her friend Tara arrived.'
        spanish_text = 'Me llamo Pedro y hoy quiero hablar del parque que hay junto a mi casa. Yo me divierto todos los días en el parque.'
        full_text_in_blocks = [english_text, spanish_text]
        self.p.strophes = full_text_in_blocks
        self.p.filter_by_language()
        self.assertEqual(self.p.strophes, [spanish_text])

    def test_filter_weak_data(self):
        string = 'This is an example that is not taken.'
        good_one = 'This text instead has enough words according to the window_size'
        self.p.strophes = [string, good_one]
        self.p.filter_weak_data()
        self.assertEqual(self.p.strophes, [good_one])

    def test_strophes_in_words(self):
        block1 = 'example text\n'
        block2 = 'another example'
        self.p.strophes = [block1, block2]
        self.p.strophes_in_words()
        self.assertEqual(self.p.strophes, [['example', 'text', '\n'], ['another', 'example']])

    def test_find_total_and_ignored_words(self):
        min_word_frequency = 2
        block1 = 'example text examples are ok\n'
        block2 = 'example text examples are not ok\n'
        block3 = 'example text examples are quite ok\n'
        self.p.strophes = [block1, block2, block3]
        self.p.strophes_in_words()
        self.p.find_total_and_ignored_words(min_word_frequency)
        self.assertEqual(len(self.p.words), 6)
        self.assertEqual(len(self.p.ignored_words), 2)
        self.assertEqual(self.p.total_words, 7)

    def test_is_valid(self):
        self.p.ignored_words = {'these', 'are', 'ignored'}
        self.assertTrue(self.p._is_valid(['this', 'is', 'ok']))
        self.assertFalse(self.p._is_valid(['this', 'is', 'ignored']))

    def test_generate_training_and_test_set(self):
        window_size = 4
        self.p.strophes = [['this', 'is', 'a', 'long', 'enough', 'text']]
        self.p.generate_training_and_test_set(window_size)
        self.assertEqual([['this', 'is', 'a', 'long'], ['is', 'a', 'long', 'enough']], self.p.x)
        self.assertEqual(['enough', 'text'], self.p.y)

    def test_serialize_processor(self):
        output_path = './output.dump'
        self.p.serialize_preprocessor(output_path)
        import os
        self.assertTrue(os.path.isfile(output_path))
        os.system('rm ' + output_path)


if __name__ == '__main__':
    unittest.main()
