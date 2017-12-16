from __future__ import print_function
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys

training_file_path = "output.txt"

text = open(training_file_path).read().lower()


max_ingredients = 5
ingredients = text.split("\n")
next_chars = []
recipes_tmp = []

different_ingredients = ingredients

ingredient_numbers = dict((c,i) for i, c in enumerate(different_ingredients))
number_ingredients = dict((i,c) for i, c in enumerate(different_ingredients))

recipes = []

for i in range(0, len(ingredients) - max_ingredients):
    recipes_tmp.append(ingredients[i: i + max_ingredients])
    next_chars.append(ingredients[i+max_ingredients])


for i in recipes_tmp:
    recipes.append("\n".join(i))


x = np.zeros((len(recipes), max_ingredients, len(ingredients)), dtype=np.bool)
y = np.zeros((len(recipes), len(different_ingredients)), dtype=np.bool)
for i, recipe in enumerate(recipes):
    for t, char in enumerate(recipe.split("\n")):
        x[i, t, ingredient_numbers[char]] = 1
    y[i, ingredient_numbers[next_chars[i]]] = 1

model = Sequential()
model.add(LSTM(128, input_shape=(max_ingredients, len(ingredients))))
model.add(Dense(len(ingredients)))
model.add(Activation('softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)

def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

for iteration in range(1,500):
    print("iteration", iteration)
    model.fit(x,y, batch_size=128, epochs=1)
    start_index = random.randint(0, len(recipes) - max_ingredients - 1)

    generated = ''
    base = "".join(recipes[start_index])
    generated += base
    print("\nSeed: " + base)
    print("\n\n")
    sys.stdout.write(generated + "\n")
    diversity = 1.0

    for i in range(15):
        x_pred = np.zeros((1, max_ingredients, len(ingredients)))
        for t, char in enumerate(base.split("\n")):
            x_pred[0, t, ingredient_numbers[char]] = 1.

        preds = model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_char = number_ingredients[next_index]
        
        generated += next_char

        base = base.split("\n")[1:]
        base.append(next_char)
        base = "\n".join(base)
        sys.stdout.write(next_char + "\n")
        sys.stdout.flush()
    print()

model.save("model.h5")
