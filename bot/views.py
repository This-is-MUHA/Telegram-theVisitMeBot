from django.shortcuts import render
from bot.apps import BotConfig
from django.http import HttpResponse

# Create your views here.
def startbot(request):
    bot = BotConfig.main()
    return HttpResponse("<h1>Bot started successfully!</h1>")