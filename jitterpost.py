import praw
import pyimgur

class jitterpost(object):
    def __init__(self):
        #Initialize the class with some basic attributes.
        self.oc = ''
        self.title = ''
        self.title_short = ''
        
    def login_imgur(self, client_id, client_secret):
        self.i = pyimgur.Imgur(client_id, client_secret=client_secret)
        return self

    def login_reddit(self, user, pw, user_agent):
        self.r = praw.Reddit(user_agent=user_agent)
        self.r.login(user, pw)
        return self

    def reddit_get_submission(self, submission_id):
        self.oc = self.r.get_submission(submission_id=submission_id)
        self.title = self.oc.title + " (from /r/"+self.oc.subreddit.display_name+ " by /u/" + self.oc.author.name + ")"
        self.title_short = self.oc.title + " (/u/" + self.oc.author.name + ")"
        self.title = self.remove_oc(self.title)
        self.title_short = self.remove_oc(self.title_short)
        return self

    def submit_imgur(self, filename):
        imgur_image = self.i.upload_image(filename, title=self.title)
        return imgur_image

    def submit_imgur_2(self, filenameA, filenameB):
        uploaded_imageA = self.i.upload_image(filenameA, title='Version A', description=self.title)
        uploaded_imageB = self.i.upload_image(filenameB, title='Version B', description=self.title)
        imgur_album = self.i.create_album(images=[uploaded_imageA, uploaded_imageB])
        return imgur_album
        
    def submit_reddit(self, subreddit, url):
        submission = self.r.submit(subreddit, self.title_short, url=url)
        return submission
        
    def comment_linking_to_oc(self, new_id):
        newSubmission = self.r.get_submission(submission_id=new_id)
        msg = ''
        msg += 'These images were automatically generated from a submission by /u/' + self.oc.author.name + ' in /r/' + self.oc.subreddit.display_name + '. '
        msg += 'Please note that there are two (2) versions in the album, one with the correct depth and the other with inverse depth, depending on how your view the images. '
        msg += 'You can find the original post here:\n\n'
        msg += '* [' + self.escape_reddit(self.oc.title) + '](' + self.oc.permalink + ')\n'
        newSubmission.add_comment(msg)
        
    def comment_oc(self, submissionAID, submissionBID):
        submissionA = self.r.get_submission(submission_id=submissionAID)
        submissionB = self.r.get_submission(submission_id=submissionBID)
        msg = ''
        msg += 'I automatically converted your image for /r/'+submissionA.subreddit.display_name+' and /r/'+submissionB.subreddit.display_name+'!\n\n'
        msg += '* ['+submissionA.subreddit.display_name+'](' + submissionA.permalink + ')\n'
        msg += '* ['+submissionB.subreddit.display_name+'](' + submissionB.permalink + ')'
        self.oc.add_comment(msg)
        self.oc.upvote()
        
    def remove_oc(self, txt):
        outText = txt.replace('[OC]','')
        outText = outText.replace('[oc]','')
        outText = outText.replace('(OC)','')
        outText = outText.replace('(oc)','')
        outText = outText.replace('{OC}','')
        outText = outText.replace('{oc}','')
        outText = outText.replace('OC','')
        outText = outText.replace('oc','')
        return outText

    def escape_reddit(self, txt):
        outText = txt.replace("*","\*")
        outText = outText.replace(">",r"\>")
        outText = outText.replace("- ",r"\- ")
        outText = outText.replace("\n1. ","\n1\. ")
        outText = outText.replace("\n2. ","\n2\. ")
        outText = outText.replace("\n3. ","\n3\. ")
        outText = outText.replace("\n4. ","\n4\. ")
        outText = outText.replace("\n5. ","\n5\. ")
        outText = outText.replace("\n6. ","\n6\. ")
        outText = outText.replace("\n7. ","\n7\. ")
        outText = outText.replace("\n8. ","\n8\. ")
        outText = outText.replace("\n9. ","\n9\. ")
        outText = outText.replace("^","\^")
        outText = outText.replace("[","\[")
        outText = outText.replace("]","\]")
        outText = outText.replace("(","\(")
        outText = outText.replace(")","\)")
        outText = outText.replace("#","\#")
        return outText