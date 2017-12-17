from keras.models import load_model
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import random
import sys
import re
import numpy as np


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

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



model = load_model("model.h5")

def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def makeRecipe(seed):
    start_index = random.randint(0, len(recipes) - max_ingredients - 1)
    if len(seed) > 0:
        r = re.compile(".*" + seed + "*.")
        matches = filter(r.match, recipes)
        if len(matches) > 0:
            start_index = recipes.index(random.choice(matches))

    generated = ''
    base = recipes[start_index]
    print(base)
    generated += base + "\n"
    diversity = 1.0
    
    for i in range(15):
        x_pred = np.zeros((1, max_ingredients, len(ingredients)))
        for t, char in enumerate(base.split("\n")):
            x_pred[0, t, ingredient_numbers[char]] = 1.
    
        preds = model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_char = number_ingredients[next_index]
    
        generated += next_char + "\n"
    
        base = base.split("\n")[1:]
        base.append(next_char)
        base = "\n".join(base)
    return generated
print(makeRecipe("paprika"))

def recept(bot, update, args):
    if args:
    	seed = makeRecipe(args[0])
    else:
	seed = makeRecipe("")
    update.message.reply_text(seed)
    

def main():
    apikey = open("APIKeyHolder.txt", "r").read()
    updater = Updater(apikey.rstrip())

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("recept", recept, pass_args=True))

    #dp.add_handler(MessageHandler(Filters.text, recept))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


