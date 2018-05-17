import bot, connectionInfo

mainBot = bot.Bot(**connectionInfo.redditConnect)
mainBot.login()

#try:
comments, submissions = mainBot.fetch_content()

for c in comments:
    mainBot.crawling_routine(c)

for s in submissions:
    mainBot.crawling_routine(s)

mainBot.timely_run()

#except:
    #print("Error fetching data")