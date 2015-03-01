from ConfigParser import SafeConfigParser
import jitterimg
import jitterpost
import jitterqueue
import matplotlib.pyplot as plt
import urllib2

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
    if ((jq.queue[uid]['anaglyph']==1) or
        (jq.queue[uid]['crossview']==1) or
        (jq.queue[uid]['wigglegram']==1)):
            
        print '\nDownloading {0} from {1}'.format(uid, jq.queue[uid]['sub'])
        jp.reddit_get_submission(uid)
        ji = jitterimg.jitterimg()
        try:
            if (jq.queue[uid]['sub'] == 'wigglegrams'):
                ji.download_wigglegram(jp.oc.url)
            elif (jq.queue[uid]['sub'] == 'crossview'):
                ji.download_crossview(jp.oc.url)
            print 'Processing images'
        except urllib2.HTTPError, e:
            if e.code == 403:
                print 'ERROR: Image download lead to 403 forbidden, removing from queue'
                jq.skip_queue(uid, jq.queue[uid]['sub'])
                jq.save_queue()
                continue
            elif e.code == 404:
                print 'ERROR: Image download lead to 404 not found, removing from queue'
                jq.skip_queue(uid, jq.queue[uid]['sub'])
                jq.save_queue()
                continue
            else:
                raise
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
                jq.skip_queue(uid, jq.queue[uid]['sub'])
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
            
        if (jq.queue[uid]['anaglyph'] == 1):
            if not 'anaglyphImgur' in jq.queue[uid]:
                print 'Submitting anaglyphs to Imgur'
                upload_i = jp.submit_imgur_2(uid+"_anaglyphA.JPG",
                                             uid+"_anaglyphB.JPG")
                print 'imgur URL: {0}'.format(upload_i.link)
                jq.queue[uid]['anaglyphImgur'] = upload_i.link
            if not 'anaglyphReddit' in jq.queue[uid]:
                print 'Submitting anaglyphs to Reddit'
                upload_r = jp.submit_reddit('Anaglyph', jq.queue[uid]['anaglyphImgur'])
                print 'reddit URL: {0}'.format(upload_r.short_link)
                jq.queue[uid]['anaglyphReddit'] = upload_r.id
            jp.comment_linking_to_oc(jq.queue[uid]['anaglyphReddit'])
            jq.queue[uid]['anaglyph'] = 0
            jq.save_queue()

        if (jq.queue[uid]['crossview'] == 1):
            if not 'crossviewImgur' in jq.queue[uid]:
                print 'Submitting crossviews to Imgur'
                upload_i = jp.submit_imgur_2(uid+"_crossviewA.JPG",
                                             uid+"_crossviewB.JPG")
                print 'imgur URL: {0}'.format(upload_i.link)
                jq.queue[uid]['crossviewImgur'] = upload_i.link
            if not 'crossviewReddit' in jq.queue[uid]:
                print 'Submitting crossviews to Reddit'
                upload_r = jp.submit_reddit('CrossView', jq.queue[uid]['crossviewImgur'])
                print 'reddit URL: {0}'.format(upload_r.short_link)
                jq.queue[uid]['crossviewReddit'] = upload_r.id
            jp.comment_linking_to_oc(jq.queue[uid]['crossviewReddit'])
            jq.queue[uid]['crossview'] = 0
            jq.save_queue()

        if (jq.queue[uid]['wigglegram'] == 1):
            if not 'wigglegramImgur' in jq.queue[uid]:
                print 'Submitting wigglegram to Imgur'
                upload_i = jp.submit_imgur(uid+"_wiggle.GIF")
                print 'imgur URL: {0}'.format(upload_i.link)
                jq.queue[uid]['wigglegramImgur'] = upload_i.link
            if not 'wigglegramReddit' in jq.queue[uid]:
                print 'Submitting wigglegram to Reddit'
                upload_r = jp.submit_reddit('Wigglegrams', jq.queue[uid]['wigglegramImgur'])
                print 'reddit URL: {0}'.format(upload_r.short_link)
                jq.queue[uid]['wigglegramReddit'] = upload_r.id
            jp.comment_linking_to_oc(jq.queue[uid]['wigglegramReddit'])
            jq.queue[uid]['wigglegram'] = 0
            jq.save_queue()
                
        if ((jq.queue[uid]['sub'] == 'wigglegrams') and
            ('anaglyphReddit' in jq.queue[uid]) and
            ('crossviewReddit' in jq.queue[uid])):
            jp.comment_oc(jq.queue[uid]['anaglyphReddit'],
                          jq.queue[uid]['crossviewReddit'])
            print 'Great Success!'
        elif ((jq.queue[uid]['sub'] == 'crossview') and
              ('anaglyphReddit' in jq.queue[uid]) and
              ('wigglegramReddit' in jq.queue[uid])):
            jp.comment_oc(jq.queue[uid]['anaglyphReddit'],
                          jq.queue[uid]['wigglegramReddit'])
            print 'Great Success!'
                
        ji.remove_all(uid)

print 'Done!'
