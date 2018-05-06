import bot

clientId = ""
secret = "Z"
userAgent = ""
username = ""
password = ""
sub = ""

mainBot = bot.Bot(clientId, secret, userAgent, username, password, sub)
mainBot.login()

#for c in mainBot.fetch_content():
#    mainBot.send_comment("testing", c)