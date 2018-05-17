import praw, datetime, os, mysql.connector, connectionInfo, time, bot
from mysql.connector import errorcode

TIME_BEFORE_KICK = 180 #180 hours

class TimelyRun:

    def __init__(self, session, conn):
        self.session = session  # the reddit instance
        self.conn = conn

        self.recap = ""

    def log(self, m):
        """  Logs a message to a file named after today's date.
            args:
                m (string): the message to log
        """
        with open(str(os.getcwd()) + str(datetime.date.today()) + ".txt", "a") as file:
            file.write(m + "\n")

        print(m)

    def run(self):
        n = self.kick_members()
        self.add_members(n)

        return self.recap

    def add_members(self, n):
        """ Add n members to the subreddit based on some criterias.
                args:
                    n (int): The number of members to add.
        """
        pass

    def kick_members(self):
        """ Kick the members who haven't posted in the last chosen number of days.

            return:
                nbKicked (int): The number of people kicked.
        """

        if (self.conn):

            kickedUsers = {}

            cursorGet = self.conn.cursor(buffered=True)  # we define 2 cursors, one to get values and the other to set
            cursorSet = self.conn.cursor(buffered=True)  # them we also make them buffered to make sure the sql
            # connector doesn't return any error while fetching data

            getUsers = ("SELECT username, previousUser, nextUser, commentDate, kicked FROM users")
            updateUsers = ("UPDATE users SET previousUser=%s, nextUser=%s, kicked=%s, dateKicked=%s WHERE username=%s")

            cursorGet.execute(getUsers)

            for (username, previousUser, nextUser, commentDate, kicked) in cursorGet:  # we fetch each users
                if (kicked == True):  # if the user is kicked, we don't want to spend time finding his infos
                    continue
                if (commentDate == "None"):
                    self.log("[NOT OK] User {} has never posted.  kicking {}".format(username, username))
                    kickedUsers[username] = previousUser + "|" + nextUser
                    self.kick(self.session.redditor(username))
                    continue

                now = datetime.datetime.fromtimestamp(time.time())  # Calulating time since last post...
                lastC = datetime.datetime.fromtimestamp(float(commentDate))
                hours = (now - lastC).total_seconds() / 3600

                if (hours > TIME_BEFORE_KICK):
                    self.log("[NOT OK] User {} has posted {} hours ago.  kicking {}".format(username,
                                                                                            round(hours, 2), username))
                    kickedUsers[username] = previousUser + "|" + nextUser
                    self.kick(self.session.redditor(username))

                else:
                    self.log("[OK] User {} has posted {} hours ago.".format(username, round(hours, 2)))

            cursorGet.close()
            cursorGet = self.conn.cursor(buffered=True)
            cursorGet.execute(getUsers)

            for (username, previousUser, nextUser, commentDate, kicked) in cursorGet:  # have to do it another time for
                # flairs.
                newPreviousUser = previousUser
                newNextUser = nextUser

                if (username in kickedUsers):
                    newKicked = True
                    newDateKicked = time.time()
                else:
                    newKicked = False
                    newDateKicked = 0

                    while (newPreviousUser in kickedUsers):  # here, we set the order of users for
                        newPreviousUser = kickedUsers[previousUser].split("|")[0]  # the flairs.
                        # previousUser and nextUser are used
                    while (newNextUser in kickedUsers):  # for us to know who goes where in
                        newNextUser = kickedUsers[nextUser].split("|")[1]  # the list for flair assignation.

                cursorSet.execute(updateUsers, (newPreviousUser, newNextUser, bool(newKicked), newDateKicked, username))
                self.conn.commit()

            cursorGet.close()
            cursorSet.close()

        else:
            self.log("Can't fetch data because you are not connected to the database!")

    def set_flair(self, member, flair, flairClass=None):
        """ Sets the flair for a member.
            args:
                member (redditor): The redditor instance whose flair to change.
                flair (text): The text of the flair.
                flairClass (text): The css class of the flair.  No class by default.
        """
        self.session.subreddit(bot.sub).flair.set(member, flair, flairClass)
        self.log("Changed {}'s flair to {}.".format(member, flair))

    def kick(self, member):
        """Kick a member.
            args:
                member (redditor): The redditor to kick.
        """
        self.session.subreddit(bot.sub).contributor.remove(member)
        self.log("Kicked {}".format(member.name))
        self.set_flair(member, "[Kicked]", "kicked")