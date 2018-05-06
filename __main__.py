import bot, connectionInfo

clientId = ""
secret = ""
userAgent = ""
username = ""
password = ""
sub = ""

mainBot = bot.Bot(**connectionInfo.redditConnect)
mainBot.login()

#for c in mainBot.fetch_content():
#    mainBot.send_comment("testing", c)