import bot, connectionInfo

mainBot = bot.Bot(**connectionInfo.redditConnect)
mainBot.login()

try:
    for c in mainBot.fetch_content():

        print(c)
        #mainBot.send_comment("testing", c)
except:
    print("Error fetching data")