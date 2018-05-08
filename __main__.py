import bot, connectionInfo

mainBot = bot.Bot(**connectionInfo.redditConnect)
mainBot.login()

try:
    comments, submissions = mainBot.fetch_content()

    for c in comments:
        print(c)

    for s in submissions:
        print(s)

except:
    print("Error fetching data")