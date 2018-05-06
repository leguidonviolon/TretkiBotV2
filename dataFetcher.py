import praw, bot
from threading import Thread

class DataFetcher(Thread):
    """This class is used to create threads to fetch reddit comments and submissions.  Threads are used because
    the PRAW streams system separates comments and submissions.  This way, we can infinitely iterate through
    both streams at the same time.
    """

    def __init__(self, ctype, session, sub):  #ctype 0 = submissions, 1 = comments
        Thread.__init__(self)
        self.type = ctype
        self.session = session
        self.sub = sub
        self.rdy = False
        self.value = None

    def run(self):
        """Function that returns the comment/submission instance of reddit streams.

        return:
            p (comment): the instance of the comment or submission
        """

        if(self.type == 0):
            for s in self.session.subreddit(self.sub).stream.submissions():
                while (1):
                    if (self.rdy == True):
                        self.value = s
                        break
                print(s)

        else:
            for c in self.session.subreddit(self.sub).stream.comments():
                while(1):
                    if(self.rdy==True):
                        self.value = c
                        break
                print(c)
