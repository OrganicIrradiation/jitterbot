import cPickle
import os

class jitterqueue(object):
    def __init__(self):
        self.path = 'jitterqueue_queue.p'
        self.r_username = ''
        self.queue = {}
    
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
            
    def skip_queue(self, submission_id):
        if submission_id not in self.queue:
            self.add_to_queue(submission_id)
        for sub in self.queue[submission_id]:
            self.queue[submission_id][sub]['process'] = False
        return self

    def add_to_queue(self, submission_id, source_sub = None):
        self.queue[submission_id] = {'anaglyph': {},
                                     'crossview': {},
                                     'parallelview': {},
                                     'wigglegrams': {}}
        for sub in self.queue[submission_id]:
            self.queue[submission_id][sub].update({'process': True,
                                                   'imgur': None,
                                                   'reddit': None,
                                                   'source': False})
        if source_sub:
            self.queue[submission_id][source_sub]['process'] = False
            self.queue[submission_id][source_sub]['source'] = True
        return self
        
    def parse_subreddit(self, r, source_sub):
        submissions = r.get_subreddit(source_sub).get_hot()
        while True:
            try:
                submission = submissions.next()
            except:
                break
        
            if (submission.id not in self.queue):
                try:
                    submission.author.name
                except AttributeError:
                    print 'Skipping {0} - Submission name invalid'.format(submission.id)
                    self.skip_queue(submission.id)
                else:
                    if submission.author.name == self.r_username:
                        print 'Skipping {0} - Submission is by {1}'.format(submission.id, submission.author.name)
                        self.skip_queue(submission.id)
                    else:
                        URL = submission.url
                        extensions = ['.JPG','.JPEG','.GIF','.PNG']
                        if any(x in URL.upper() for x in extensions):
                            print '   Added {0}'.format(submission.id)
                            self.add_to_queue(submission.id, source_sub)
                        else:
                            print 'Skipping {0} - Submission was not an image'.format(submission.id)
                            self.skip_queue(submission.id)
