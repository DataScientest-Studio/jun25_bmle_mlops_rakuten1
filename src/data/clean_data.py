import pandas as pd

from clean_text import clean_text


X_train = pd.read_csv('input/X_train_update.csv')
y_train = pd.read_csv('input/Y_train_CVw08PX.csv')
X_test = pd.read_csv('input/X_test_update.csv')

X_train.to_csv('output/data.csv', index=False)
