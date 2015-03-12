from ConfigParser import SafeConfigParser
import jitterimg
import jitterpost
import jitterqueue
import matplotlib.pyplot as plt
import urllib2

def process_data(subreddit, uid):
    if subreddit == 'anaglyph':
        filename = uid+"_anaglyph.JPG"
    elif subreddit == 'crossview':
        filename = uid+"_crossview.JPG"
    elif subreddit == 'parallelview':
        filename = uid+"_parallelview.JPG"
    elif subreddit == 'wigglegram':
        filename = uid+"_wiggle.GIF"

    if jq.queue[uid][subreddit]['process']:
        print 'Submitting to Imgur'.format(subreddit)
        upload_i = jp.submit_imgur(filename)
        print 'imgur URL: {0}'.format(upload_i.link)
        jq.queue[uid][subreddit]['imgur'] = upload_i.link

        print 'Submitting to Reddit'
        upload_r = jp.submit_reddit(subreddit, jq.queue[uid][subreddit]['imgur'])
        print 'reddit URL: {0}'.format(upload_r.short_link)
        jq.queue[uid][subreddit]['reddit'] = upload_r.id

        jp.comment_linking_to_oc(jq.queue[uid][subreddit]['reddit'])
        jq.queue[uid][subreddit]['process'] = False
        jq.save_queue()

# Get the user information from the configuration file
config = SafeConfigParser()
config.read('config.ini')

jp = jitterpost.jitterpost()
jq = jitterqueue.jitterqueue()

print 'Logging into Reddit'
jp.login_reddit(config.get('reddit', 'username'),
                config.get('reddit', 'password'),
                config.get('reddit', 'user_agent'))

print 'Logging into imgur'
jp.login_imgur(config.get('imgur', 'client_id'),
               config.get('imgur', 'client_secret'))

jq.r_username = config.get('reddit', 'username')
print 'Loading queue'
jq.load_queue()

print 'Updating queue for wigglegrams'
jq.parse_subreddit(jp.r, 'wigglegrams')
jq.save_queue()

print 'Updating queue for crossview'
jq.parse_subreddit(jp.r, 'crossview')
jq.save_queue()

for uid in jq.queue:
    if (True in [jq.queue[uid][sub]['process'] for sub in jq.queue[uid]]):
        source_sub = [sub for sub in jq.queue[uid] if jq.queue[uid][sub]['source'] == True][0]
        print '\nDownloading {0} from {1}'.format(uid, source_sub)
        jp.reddit_get_submission(uid)
        ji = jitterimg.jitterimg()
        try:
            if (source_sub == 'wigglegrams'):
                ji.download_wigglegram(jp.oc.url)
            elif (source_sub == 'crossview'):
                ji.download_crossview(jp.oc.url)
            print 'Processing images'
        except urllib2.HTTPError, e:
            if e.code == 403:
                print 'ERROR: Image download lead to 403 forbidden, removing from queue'
                jq.skip_queue(uid)
                jq.save_queue()
                continue
            elif e.code == 404:
                print 'ERROR: Image download lead to 404 not found, removing from queue'
                jq.skip_queue(uid)
                jq.save_queue()
                continue
            else:
                raise
        except ji.FiletypeUnknown, filetype:
            print 'ERROR: Filetype unknown or incompatible: {0}'.format(filetype)
            jq.skip_queue(uid)
            jq.save_queue()
            continue
        ji.save_all(uid)
 
        print u'Original: {0}\nLong: {1}\nShort: {2}'.format(jp.oc.title, jp.title, jp.title_short)
        fig = plt.figure(0)
        ax1 = fig.add_subplot(211)
        ax1.imshow(ji.crossview())
        ax2 = fig.add_subplot(212)
        ax2.imshow(ji.swap_lr().crossview())
        plt.draw()
        plt.show(block=False)
        ji.swap_lr()
        
        inputVar = raw_input("Submit? (Y/N/Q) ")
        if inputVar.upper() == 'N':
            inputVar = raw_input("Add to skip list? (Y/N) ")
            if inputVar.upper() == 'Y':
                jq.skip_queue(uid)
                jq.save_queue()
            ji.remove_all(uid)
            continue
        elif inputVar.upper() == 'Q':
            ji.remove_all(uid)
            break

        inputVar = raw_input("Swap left/right images (make sure Version A is crossview!)? (Y/N) ")
        if inputVar.upper() == 'Y':
            ji.swap_lr()
            print 'Re-processing images'
            ji.save_all(uid)

        process_data('anaglyph', uid)
        process_data('crossview', uid)
        process_data('parallelview', uid)
        process_data('wigglegrams', uid)
        
        if (source_sub == 'anaglyph'):
            jp.comment_oc(jq.queue[uid]['crossview']['reddit'],
                          jq.queue[uid]['parallelview']['reddit'],
                          jq.queue[uid]['wigglegrams']['reddit'])
        elif (source_sub == 'crossview'):
            jp.comment_oc(jq.queue[uid]['anaglyph']['reddit'],
                          jq.queue[uid]['parallelview']['reddit'],
                          jq.queue[uid]['wigglegrams']['reddit'])
        elif (source_sub == 'parallelview'):
            jp.comment_oc(jq.queue[uid]['anaglyph']['reddit'],
                          jq.queue[uid]['crossview']['reddit'],
                          jq.queue[uid]['wigglegrams']['reddit'])
        elif (source_sub == 'wigglegrams'):
            jp.comment_oc(jq.queue[uid]['anaglyph']['reddit'],
                          jq.queue[uid]['crossview']['reddit'],
                          jq.queue[uid]['parallelview']['reddit'])
        print 'Great Success!'
                
        ji.remove_all(uid)

print 'Done!'
