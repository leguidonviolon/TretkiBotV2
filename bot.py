import praw, datetime, os, mysql.connector, connectionInfo
from mysql.connector import errorcode

class Bot:

    def __init__(self, clientid, secret, user_agent, username, password, sub):
        self.clientId = clientid
        self.secret = secret
        self.userAgent = user_agent
        self.username = username
        self.password = password
        self.sub = sub

        self.session = None  # the reddit instance

        try:
            self.conn = mysql.connector.connect(**connectionInfo.sqlConnect)
        except mysql.connector.Error as e:
            if(e.errno==errorcode.ER_ACCESS_DENIED_ERROR):
                print("Wrong username/password combination")
            elif(e.errno==errorcode.ER_BAD_DB_ERROR):
                print("Database doesn't exist")
            else:
                print(e)

    def login(self):
        """  Login to reddit with the bot.
            Sets the session variable to the reddit instance.
        """
        try:
            self.log("Logging in reddit...")
            reddit = praw.Reddit(client_id=self.clientId, client_secret=self.secret, user_agent=self.userAgent,
                             username=self.username, password=self.password)
        except:
            self.log("Couldn't log in.")
        else:
            self.log("Logged in!")
            self.session = reddit



    def log(self, m):
        """  Logs a message to a file named after today's date.
            args:
                m (string): the message to log
        """
        with open(str(os.getcwd()) + str(datetime.date.today()) + ".txt", "a") as file:
            file.write(m + "\n")

        print(m)

    def send_submission(self, title, text, mod=False):
        """ Post a normal submission to the session's subreddit instance.
            args:
                title (string): The title of the post.
                text (string): The body of the post.
                mod (bool): Used by the make_mod_post function.  If set to True, we don't log things in this function.

            return:
                p (submission): If the submission is sent successfully, it returns the submission's instance.
                string: If the submission failed to be posted, we return an error.
        """
        try:
            p = self.session.subreddit(self.sub).submit(title, text)
            if mod==False: # then, we log the required information
                self.log("Posted submission with title " + title + " and post_id: " + p.fullname)
            return p
        except:
            if mod==False: #then, we log the required information
                self.log("Couldn't post to reddit")
            return "Couldn't post to reddit."

    def make_mod_post(self, title, text, flair="", sticky=False):
        """ Post a distinguished submission to the session's subreddit instance.
                args:
                    title (string): The title of the post.
                    text (string): The body of the post.
                    flair (text): The flair of the submission.
                    sticky (bool): required if we want to sticky the submission.

                return:
                    p (submission): If the submission is sent successfully, it returns the submission's instance.
                    string: If the submission failed to be posted, we return an error.
        """
        try:
            p = self.send_submission(title, text, True) #mod is set to true, so we don't log in send_submission
            p.mod.distinguish('yes')
            if(sticky==True):
                p.mod.sticky()
            p.mod.flair(text=flair)
            self.log("Posted mod post with title " + title + " and post_id: " + p.fullname) #we log here instead
            return p
        except:
            self.log("Couldn't post to reddit")
            return "Couldn't post to reddit."

    def send_comment(self, text, c):
        """ Post a comment to the session's subreddit instance.
                args:
                    text (string): The body of the comment.
                    c (submission): The submission or comment instance we want to reply to.

                return:
                    p (comment): If the comment is sent successfully, it returns the comment's instance.
                    string: If the comment failed to be posted, we return an error.
        """
        try:
            if(c.author!=self.username):
                c.reply(text)
            else:
                print("Couldn't reply to own comment.")
        except:
            print("Couldn't comment.")


    def make_mod_comment(self, text, sticky=False):
        pass

    def fetch_content(self):
        """ Fetches all the last comments and submissions of the subreddit and returns two lists containing them.
                return:
                    comments (list): the list of all the fetched comments
                    submissions (list): the list of all the fetched submissions
        """

        comments = []
        submissions = []

        if(self.conn):
            cursor = self.conn.cursor()

            query = ("SELECT lastCommentChecked, lastPostChecked FROM botInfo")

            cursor.execute(query)

            for (lastCommentChecked, lastPostChecked) in cursor:
                lastCommentId = lastCommentChecked
                lastSubmissionId = lastPostChecked

            newCommentId = ""
            newSubmissionId = ""

            for c in self.session.subreddit(self.sub).comments():
                if(newCommentId==""):
                    newCommentId = c.id

                if (c.id==lastCommentId):
                    break

                comments.append(c)

            for s in self.session.subreddit(self.sub).new():
                if(newSubmissionId==""):
                    newSubmissionId = s.id

                if(s.id==lastSubmissionId):
                    break

                submissions.append(s)

            query = ("UPDATE botInfo SET lastPostChecked=%s, lastCommentChecked=%s")

            cursor.execute(query, (newSubmissionId, newCommentId))

            self.conn.commit()
            cursor.close()

            return comments, submissions
        else:
            print("Can't fetch data because the database isn't connected!")


    def __repr__(self):
        self.__str__()

    def __str__(self):
        if self.session != None:
            return "Signed in as " + self.username
        else:
            return "Bot isn't signed in!"