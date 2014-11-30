pyJitterBot.py
==========================

This is the script used to run [/u/JitterBot](https://www.reddit.com/user/JitterBot/) on reddit.com.  It automatically converts crossview stereograms to anaglyph and wigglegram images and wigglegrams to anaglyphs and crossviews.

It would be nice to autonomously, but it currently opperates as a script that I occasionally run (to avoid spamming the subreddits and manually doing some quality control for the generated images).

The basic workflow is:

 1. Load the hot submission lists for [/r/CrossView](https://www.reddit.com/r/CrossView) and [/r/wigglegrams](https://www.reddit.com/r/wigglegrams) and add links that directly point to images to a processing queue.
 2. Download the top entry in the queue
 3. If it is a wigglegram, use the first and middle frames as the left and right images for the image pair.  If it is a crossview image, split the image in half.
 4. Save the images locally and request feedback about whether or not to submit (for quality control)
 5. If everything looks good, submit the images to imgur and the imgur links to Reddit
 6. Repeat
 
##Setup
Note that you will need to create a config.ini file with a reddit login and an imgur login.  There is an example in the repo.
 
##Prerequisites
Tested with Python 2.7.8 and the following libraries (tested versions in parentheses):

  * Pillow (2.6.1)
  * praw (2.1.19)
  * pyimgur (0.5.2)

Note that a version of images2gif that works with the pyJitterBot.py code is also included because the PyPI version has unresolved issues. 
