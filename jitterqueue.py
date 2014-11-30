import cPickle
import collections
import os

class jitterqueue(object):
    def __init__(self):
        self.path = 'jitterqueue_queue.p'
        self.r_username = ''
        self.queue = collections.OrderedDict()
    
    def load_queue(self, **kwargs):
        path = kwargs.get('path', self.path)
        if os.path.isfile(path):
            self.path = path
            self.queue = cPickle.load(open(path, 'rb'))
        return self
    
    def save_queue(self, **kwargs):
        path = kwargs.get('path', self.path)
        cPickle.dump(self.queue, open(path, 'wb'))
        return self
            
    def skip_queue(self, submission_id, sub):
        self.queue[submission_id] = {}
        self.queue[submission_id]['anaglyph'] = 0
        self.queue[submission_id]['crossview'] = 0
        self.queue[submission_id]['wigglegram'] = 0
        self.queue[submission_id]['sub'] = sub
        return self

    def add_to_queue(self, submission_id, sub, anaglyph, crossview, wigglegram):
        self.queue[submission_id] = {}
        self.queue[submission_id]['anaglyph'] = anaglyph
        self.queue[submission_id]['crossview'] = crossview
        self.queue[submission_id]['wigglegram'] = wigglegram
        self.queue[submission_id]['sub'] = sub
        return self
        
    def parse_subreddit(self, r, sub):
        submissions = r.get_subreddit(sub).get_hot()
        while True:
            try:
                submission = submissions.next()
            except:
                break
        
            if (submission.id not in self.queue):
                try:
                    submission.author.name
                except AttributeError:
                    print 'Skipping {0} - Submission name invalid, adding to skip list'.format(submission.id)
                    self.skip_queue(str(submission.id), sub)
                else:
                    if submission.author.name == self.r_username:
                        print 'Skipping {0} - Submission is by {1}, adding to skip list'.format(submission.id, submission.author.name)
                        self.skip_queue(str(submission.id), sub)
                    else:
                        URL = submission.url
                        extensions = ['.JPG','.JPEG','.GIF','.PNG']
                        if any(x in URL.upper() for x in extensions):
                            print '   Added {0}'.format(submission.id)
                            if (sub == 'wigglegrams'):
                                self.add_to_queue(str(submission.id), sub, 1, 1, 0)
                            elif (sub == 'crossview'):
                                self.add_to_queue(str(submission.id), sub, 1, 0, 1)
                        else:
                            print 'Skipping {0} - Submission was not an image, adding to skip list'.format(submission.id)
                            self.skip_queue(str(submission.id), sub)