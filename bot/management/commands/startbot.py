from django.core.management.base import BaseCommand, CommandError
from bot.apps import BotConfig

class Command(BaseCommand):
	help = 'Starts the bot'

	def handle(self, *args, **options):
		bot = BotConfig.main()