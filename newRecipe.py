from keras.models import load_model
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import random
import sys
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

def makeRecipe():
    start_index = random.randint(0, len(recipes) - max_ingredients - 1)

    generated = ''
    base = "".join(recipes[start_index])
    generated += base
    #sys.stdout.write(generated + "\n")
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
        #sys.stdout.write(next_char + "\n")
        #sys.stdout.flush()
    return generated

def recept(bot, update):
    update.message.reply_text(makeRecipe())

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater("372664567:AAHckAc1ZkuCXzazZYWulk-T6scbaU5gEzo")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("recept", recept))

    #dp.add_handler(MessageHandler(Filters.text, makeRecipe))
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


main()

