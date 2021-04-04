import argparse
import dill
import os
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from preprocessor import Preprocessor
from constants import *


def generator(sentence_list, next_word_list, window_size, tokenizer, batch_size):
    index = 0
    while True:
        x = np.zeros((batch_size, window_size), dtype=np.int32)
        y = np.zeros(batch_size, dtype=np.int32)
        for i in range(batch_size):
            line = sentence_list[index % len(sentence_list)]
            token_list = tokenizer.texts_to_sequences([line])[0]
            for t, w in enumerate(token_list):
                x[i, t] = w
            y[i] = tokenizer.word_index[next_word_list[index % len(sentence_list)]]
            index = index + 1
        yield x, y


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="this script generates the model using a lyrics dataset."
    )

    parser.add_argument("-p", "--preprocessor_path",
                        help="serialized preprocessor object",
                        type=str,
                        default='../data/preprocessing/preprocessor.dump')

    parser.add_argument("-o", "--output_path",
                        help="where to store model checkpoints.",
                        type=str,
                        default='../data/training/cp.ckpt')

    args = parser.parse_args()
    preprocessor_path = args.preprocessor_path
    output_path = args.output_path

    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    with open(preprocessor_path, 'rb') as file:
        p: Preprocessor = dill.load(file)

    model = Sequential()
    model.add(Embedding(input_dim=p.total_words, output_dim=1024))
    model.add(Bidirectional(LSTM(256)))
    model.add(Dropout(0.2))
    model.add(Dense(p.total_words, activation='softmax'))
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    checkpoint = ModelCheckpoint(output_path, monitor='loss', save_best_only=True, verbose=1, mode='auto')
    callbacks_list = [checkpoint]

    model.fit_generator(
        generator(p.x, p.y, WINDOW_SIZE, p.tokenizer, BATCH_SIZE),
        steps_per_epoch=int(len(p.x) / BATCH_SIZE) + 1,
        epochs=EPOCHS,
        verbose=FIT_VERBOSITY,
        callbacks=callbacks_list
    )
