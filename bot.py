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

        self.conn = self.connect_to_database()

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

    def send_mod_post(self, title, text, flair="", sticky=False):
        """ Post a distinguished submission to the session's subreddit instance.
                args:
                    title (string): The title of the post.
                    text (string): The body of the post.
                    flair (text): The flair of the submission.
                    sticky (bool): Required if we want to sticky the submission.

                return:
                    p (submission): If the submission is sent successfully, it returns the submission's instance.
                    string: If the submission failed to be posted, we return an error.
        """
        try:
            p = self.send_submission(title, text, True) #mod is set to true, so we don't save logs in send_submission
            p.mod.distinguish('yes')
            if(sticky==True):
                p.mod.sticky()
            p.mod.flair(text=flair)
            self.log("Posted mod post with title " + title + " and post_id: " + p.fullname) #we log here instead
            return p
        except:
            self.log("Couldn't post to reddit")
            return "Couldn't post to reddit."

    def send_comment(self, text, c, mod=False):
        """ Post a comment to the session's subreddit instance.
                args:
                    text (string): The body of the comment.
                    c (submission): The submission or comment instance we want to reply to.
                    mod (bool): Used by the make_mod_comment function.  If set to True, we
                    don't log things in this function.

                return:
                    p (comment): If the comment is sent successfully, it returns the comment's instance.
                    string: If the comment failed to be posted, we return an error.
        """
        try:
            if(c.author!=self.username):  # we don't want the bot to reply to itself...
                p = c.reply(text)
                if(mod==False):  # then, we log the required information
                    self.log("Posted comment with comment_id: " + p.fullname)
                return p
            else:
                return "Couldn't reply to own comment."
        except:
            return "Couldn't comment."


    def send_mod_comment(self, text, c, sticky=False):
        """ Post a distinguished comment to the session's subreddit instance.
                args:
                    text (string): The body of the comment.
                    c (submission): The submission or comment instance we want to reply to.
                    sticky (bool): Required if we want to sticky the comment.

                return:
                    p (comment): If the comment is sent successfully, it returns the comment's instance.
                    string: If the comment failed to be posted, we return an error.
                """
        try:
            p = self.send_comment(text, c, True)  # mod is set to true, so we don't save logs in send_comment
            p.mod.distinguish(sticky=sticky)
            #if (sticky == True):
                #if(isinstance(c, praw.models.Submission)):
                   # p.mod.sticky()
                #else:
                    #print("Can't sticky a comment that isn't top level.")
            self.log("Posted mod comment with comment_id: " + p.fullname)  # we log here instead
            return p
        except:
            self.log("Couldn't post to reddit")
            return "Couldn't post to reddit."

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

            for (lastCommentChecked, lastPostChecked) in cursor: # we set fetch the last comment and submission the bot
                lastCommentId = lastCommentChecked               # crawled
                lastSubmissionId = lastPostChecked

            newCommentId = ""
            newSubmissionId = ""

            for c in self.session.subreddit(self.sub).comments():
                if(newCommentId==""): # if it's the first comment we fetch, we set it as a marker for next time
                    newCommentId = c.id

                if (c.id==lastCommentId): # if this comment has already been fetched, it means we are now up to date
                    break

                comments.append(c)

            for s in self.session.subreddit(self.sub).new():
                if(newSubmissionId==""): # same as above
                    newSubmissionId = s.id

                if(s.id==lastSubmissionId): #same as above
                    break

                submissions.append(s)

            query = ("UPDATE botInfo SET lastPostChecked=%s, lastCommentChecked=%s")

            cursor.execute(query, (newSubmissionId, newCommentId)) # we send these new markers to the database

            self.conn.commit()
            cursor.close()

        else:
            print("Can't fetch data because you are not connected to the database!")

        return comments, submissions

    def crawling_routine(self, c):
        """ This function does all the things we want to do on every comment or submission, like update each member's
        last post and such.
                args:
                    c (comment):  The comment or submission to check
        """

        if(self.conn):
            cursor = self.conn.cursor()
            user = c.author.name
            commentId = c.fullname

            query = ("UPDATE users SET lastComment=%s WHERE username=%s")

            cursor.execute(query, (commentId, user)) # send the last comment id to the database for the comment's user

            self.conn.commit()


            cursor.close()

        self.easter_eggs(c)

    def connect_to_database(self):
        """ Connects to the database.
                return:
                    conn (MySqlConnection): The connection to the MySQL database.
                    False if the connection is unsuccessful"""
        try:
            conn = mysql.connector.connect(**connectionInfo.sqlConnect)
            return conn
        except mysql.connector.Error as e:
            if(e.errno==errorcode.ER_ACCESS_DENIED_ERROR):
                print("Wrong username/password combination")
            elif(e.errno==errorcode.ER_BAD_DB_ERROR):
                print("Database doesn't exist")
            else:
                print(e)
            return False

    def easter_eggs(self, c):
        """ Passes a comment or submission to all the easter eggs to see if it triggers any.
                args:
                    c (comment): The comment or submission instance to test.
        """
        self.egg_negative_karma(c)

    def egg_negative_karma(self, c):
        """ If a comment or submission has negative karma, the bot teases the user.
            args:
                c (comment): The comment or submission to test.
        """

        if(c.score<0):
            self.send_comment("Hey, you are one of the rare few who get to be downvoted "
                              "to hell in /r/{}, congrats!".format(self.sub), c)
    def __repr__(self):
        self.__str__()

    def __str__(self):
        if self.session != None:
            return "Signed in as " + self.username
        else:
            return "Bot isn't signed in!"