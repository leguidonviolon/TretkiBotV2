import bot

clientId = "6tXWCHwA0z2M6A"
secret = "ZwG0-7C2fdVZJYxMf1IU82K5_RQ"
userAgent = "TretkiBotV2:v1.0.0 (by /u/oniixon)"
username = "TretkiBot"
password = "cnpL2M1q"
sub = "TRETKIBOT"

mainBot = bot.Bot(clientId, secret, userAgent, username, password, sub)
mainBot.login()

#for c in mainBot.fetch_content():
#    mainBot.send_comment("testing", c)