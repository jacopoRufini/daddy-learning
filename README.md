# Daddy Learning (or Machine Yankee)
## An AI that generates reggaeton lyrics

![Build Status](https://img.shields.io/badge/python-v3.7-blue)

Daddy learning is a side project I've made to learn a bit more about neural networks theory and its libraries.
I've also posted on Medium about this experience, [check it out](https://jacoporufini.medium.com/daddy-learning-or-machine-yankee-an-artificial-intelligence-ai-that-generates-reggaeton-lyrics-fc2e690e9d6c).

It would be great if you could leave any feedback to improve it, I still have to learn so much stuff about this world.

## Installation

This app requires [Python3.7](https://www.python.org/downloads/)
Install the dependencies using [Poetry](https://python-poetry.org/docs/)

```sh
cd daddy-learning
poetry install
poetry shell
cd reggaeton
```
Once inside the reggaeton directory, there will be different scripts:
```sh
 # Here you can set some global variables that will be used for training / predicting
vim constants.py

# Uses the list of artists, stored in the repo, to download any song that it can find.
# This can take a bit of time
python3 ingestion.py

# Uses the data just downloaded to do some preprocessing and prepare the dataset for the training process
python3 preprocessor.py

# Uses keras APIs to train the AI based on the output of preprocessor.py. 
python3 training.py

# Uses the model just created to output some cool spanish text.
# It requires an input as large as the WINDOW_SIZE found in constants.py
python3 write.py 
```
