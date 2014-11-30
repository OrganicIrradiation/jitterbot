import cStringIO
from images2gif import writeGif
import imghdr
import math
import os
import os.path
from PIL import Image, ImageFile, ImageSequence
import urllib2

ImageFile.LOAD_TRUNCATED_IMAGES = True

# https://github.com/miguelgrinberg/anaglyph.py/blob/master/anaglyph.py
jitterbot_anaglyph_matrices = {
    'true': [ [ 0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0.299, 0.587, 0.114 ] ],
    'mono': [ [ 0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0.299, 0.587, 0.114, 0.299, 0.587, 0.114 ] ],
    'color': [ [ 1, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
    'halfcolor': [ [ 0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
    'optimized': [ [ 0, 0.7, 0.3, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 1, 0, 0, 0, 1 ] ],
}

class jitterimg(object):
    def __init__(self):
        #Initialize the class with some basic attributes.
        self.imgA = '';
        self.imgB = '';
        
    def download_crossview(self, url):
        f = cStringIO.StringIO(urllib2.urlopen(url).read())
        img_type = imghdr.what(f)
        if (img_type == 'gif') or (img_type == 'png') or (img_type == 'jpg'):
            img = Image.open(f).convert('RGB')
            w, h = img.size
            w = int(math.floor(w/2)*2)
        self.imgA = img.crop((0, 0, w/2, h))
        self.imgB = img.crop((w/2, 0, w, h))
        return self

    def download_wigglegram(self, url):
        f = cStringIO.StringIO(urllib2.urlopen(url).read())
        img_type = imghdr.what(f)
        if img_type == 'gif':
            img = Image.open(f)
            frames = [frame.copy().convert('RGB') for frame in ImageSequence.Iterator(img)]
        self.imgA = frames[0]
        self.imgB = frames[len(frames)//2]
        return self
        
    def anaglyph(self):
        left = self.imgA.copy()
        right = self.imgB.copy()
        color = 'optimized'
        width, height = left.size
        leftMap = left.load()
        rightMap = right.load()
        m = jitterbot_anaglyph_matrices[color]
        for y in range(0, height):
            for x in range(0, width):
                r1, g1, b1 = leftMap[x, y]
                r2, g2, b2 = rightMap[x, y]
                leftMap[x, y] = (
                    int(r1*m[0][0] + g1*m[0][1] + b1*m[0][2] + r2*m[1][0] + g2*m[1][1] + b2*m[1][2]),
                    int(r1*m[0][3] + g1*m[0][4] + b1*m[0][5] + r2*m[1][3] + g2*m[1][4] + b2*m[1][5]),
                    int(r1*m[0][6] + g1*m[0][7] + b1*m[0][8] + r2*m[1][6] + g2*m[1][7] + b2*m[1][8])
                )
        return left
    
    def wigglegram(self):
        return [self.imgA, self.imgB]
    
    def crossview(self):
        w, h = self.imgA.size
        w *= 2
        image_out = Image.new("RGB", (w, h))
        image_out.paste(self.imgA, (0,0))
        image_out.paste(self.imgB, (w/2,0))
        return image_out
    
    def swap_lr(self):
        self.imgA, self.imgB = self.imgB, self.imgA
        return self

    def save_all(self, filename):
        self.remove_all(filename)
        self.anaglyph().save(filename+"_anaglyphA.JPG")
        self.swap_lr().anaglyph().save(filename+"_anaglyphB.JPG")
        self.swap_lr().crossview().save(filename+"_crossviewA.JPG")
        self.swap_lr().crossview().save(filename+"_crossviewB.JPG")
        writeGif(filename+"_wiggle.GIF", self.swap_lr().wigglegram(), duration=0.1, dither=1)

    def remove_all(self, filename):
        if os.path.isfile(filename+"_anaglyphA.JPG"):
            os.remove(filename+"_anaglyphA.JPG")
        if os.path.isfile(filename+"_anaglyphB.JPG"):
            os.remove(filename+"_anaglyphB.JPG")
        if os.path.isfile(filename+"_crossviewA.JPG"):
            os.remove(filename+"_crossviewA.JPG")
        if os.path.isfile(filename+"_crossviewB.JPG"):
            os.remove(filename+"_crossviewB.JPG")
        if os.path.isfile(filename+"_wiggle.GIF"):
            os.remove(filename+"_wiggle.GIF")
