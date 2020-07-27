from django.apps import AppConfig
from django.db.utils import IntegrityError
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import redis
import pickle

class BotConfig(AppConfig):
	name = 'bot'
	r = redis.Redis()
	cache = dict()
	ADDRESS, PHOTO, LOCATION = range(3)

	def start(update, context):
		update.message.reply_text("Hi! I will help you to save your favourite places to visit at the future:) Type /add to start adding your places.")
		
	def add(update, context):
		update.message.reply_text("To add new place to visit, first send me the address of that place.")
		return BotConfig.ADDRESS

	def add_address(update, context):
		BotConfig.cache[update.message.from_user.id] = dict()
		BotConfig.cache[update.message.from_user.id]['address'] = update.message.text
		update.message.reply_text("Now send me the photo of that place.")
		return BotConfig.PHOTO

	def add_photo(update, context):
		BotConfig.cache[update.message.from_user.id]['photo'] = update.message.photo[-1]
		update.message.reply_text("Now send me the location of that place.")
		return BotConfig.LOCATION

	def add_location(update, context):
		BotConfig.cache[update.message.from_user.id]['location'] = update.message.location
		if BotConfig.r.exists(update.message.from_user.id):
			place = pickle.loads(BotConfig.r.get(update.message.from_user.id))
			place.append(BotConfig.cache[update.message.from_user.id])
			BotConfig.r.set(update.message.from_user.id, pickle.dumps(place))
		else:
			BotConfig.r.set(update.message.from_user.id, pickle.dumps([BotConfig.cache[update.message.from_user.id]]))
		update.message.reply_text("Your place to visit is saved!")
		return ConversationHandler.END

	def cancel(update, context):
		BotConfig.cache.pop(update.message.from_user.id, None)
		update.message.reply_text("Addition of new place to visit is cancelled.")
		return ConversationHandler.END

	def get_list(update, context):
		if BotConfig.r.exists(update.message.from_user.id):
			result = pickle.loads(BotConfig.r.get(update.message.from_user.id))
			if len(result) > 10:
				result = result[:-10]
			for i in range(len(result)):
				update.message.reply_text(f"Place #{i+1}")
				update.message.reply_text(result[i]['address'])
				update.message.reply_photo(result[i]['photo'])
				update.message.reply_location(location=result[i]['location'])
		else:
			update.message.reply_text("You don't have any saved places to visit:(")

	def reset(update, context):
		BotConfig.r.delete(update.message.from_user.id)
		update.message.reply_text("Your saved places to visit has been deleted.")


	@staticmethod
	def main():
		token = "1106138413:AAGQRknL_iQf-wCo9WWMwagqnFLExz9cFT4"
		updater = Updater(token, use_context=True)

		dp = updater.dispatcher

		dp.add_handler(CommandHandler('start', BotConfig.start))
		
		conv_handler = ConversationHandler(

			entry_points=[CommandHandler('add', BotConfig.add)],

			states={

				BotConfig.ADDRESS: [MessageHandler(Filters.text, BotConfig.add_address)],

				BotConfig.PHOTO: [MessageHandler(Filters.photo, BotConfig.add_photo)],

				BotConfig.LOCATION: [MessageHandler(Filters.location, BotConfig.add_location)]

			},

			fallbacks=[CommandHandler('cancel', BotConfig.cancel)]
		)

		dp.add_handler(conv_handler)

		dp.add_handler(CommandHandler('list', BotConfig.get_list))

		dp.add_handler(CommandHandler('reset', BotConfig.reset))

		updater.start_polling()