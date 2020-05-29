import tensorflow.keras as keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import sklearn.model_selection

def create_model():
    model = Sequential()
    model.add(Dense(128, input_dim=27, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    return model


def train_model(model, X, y):
    X, _, y, __ = sklearn.model_selection.train_test_split(X, y, test_size=0.00001, random_state=42)
    history = model.fit(X, y, epochs=6)
    return model


def predict(model, X):
    y_pred = model.predict(X)
    return y_pred
