#final cleaned version of the function
# param - frameRate,method, youtubeUrl
#need to decide what to do with frame once marked- discuss in meeting
#make number of duplicates parametrizable?

#need to pip install pafy and youtube-dl
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import math
import pafy
from skimage.metrics import structural_similarity as ssim

from scipy.stats import mode

def compare_images(imageA, imageB):
  s = ssim(imageA, imageB)
  return s

def uniqueFrames(videoUrl,framerate=15,method='cv.TM_CCOEFF',isYoutubeUrl=True):
    frame_list=[]
    args={'record':False,'pyr_scale':0.5,'levels':3,'winsize':15,'iterations':3,'poly_n':5,'poly_sigma':1.1,'threshold':10,'plot':False,'rgb':False,'size':10}
    frameRate=framerate
    scrollInit=False
    fadeInit=False
    dupCount=1
    directions_map = np.zeros([args['size'], 5])
    meth=method
    i=0
    print(isYoutubeUrl)
    if isYoutubeUrl:
      url = videoUrl
      videoPafy = pafy.new(url)
      vidurl = videoPafy.getbest(preftype="mp4")
      cap = cv.VideoCapture(vidurl.url)
    else:
      vidurl=videoUrl
      cap = cv.VideoCapture(vidurl)
    frameId=cap.get(1)

    frame_previous = cap.read()[1]
    gray_previous = cv.cvtColor(frame_previous, cv.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame_previous)
    hsv[:, :, 1] = 255
    param = {
        'pyr_scale': args['pyr_scale'],
        'levels': args['levels'],
        'winsize': args['winsize'],
        'iterations': args['iterations'],
        'poly_n': args['poly_n'],
        'poly_sigma': args['poly_sigma'],
        'flags': cv.OPTFLOW_LK_GET_MIN_EIGENVALS
    }

    while True:
        frameId=cap.get(1)
        grabbed, frame = cap.read()
        
        if not grabbed:
            break
        if (frameId % math.floor(frameRate) == 0):
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            flow = cv.calcOpticalFlowFarneback(gray_previous, gray, None, **param)
            mag, ang = cv.cartToPolar(flow[:, :, 0], flow[:, :, 1], angleInDegrees=True)
            ang_180 = ang/2
            gray_previous = gray
            
            move_sense = ang[mag > args['threshold']]
            move_mode = mode(move_sense)[0]

            if 10 < move_mode <= 100:
                directions_map[-1, 0] = 1
                directions_map[-1, 1:] = 0
                directions_map = np.roll(directions_map, -1, axis=0)
            elif 100 < move_mode <= 190:
                directions_map[-1, 1] = 1
                directions_map[-1, :1] = 0
                directions_map[-1, 2:] = 0
                directions_map = np.roll(directions_map, -1, axis=0)
            elif 190 < move_mode <= 280:
                directions_map[-1, 2] = 1
                directions_map[-1, :2] = 0
                directions_map[-1, 3:] = 0
                directions_map = np.roll(directions_map, -1, axis=0)
            elif 280 < move_mode or move_mode < 10:
                directions_map[-1, 3] = 1
                directions_map[-1, :3] = 0
                directions_map[-1, 4:] = 0
                directions_map = np.roll(directions_map, -1, axis=0)
            else:
                directions_map[-1, -1] = 1
                directions_map[-1, :-1] = 0
                directions_map = np.roll(directions_map, 1, axis=0)


            loc = directions_map.mean(axis=0).argmax()
            if loc == 0:
                text = 'Moving down'
            elif loc == 1:
                text = 'Moving to the right'
            elif loc == 2:
                text = 'Moving up'
            elif loc == 3:
                text = 'Moving to the left'
            else:
                text = 'WAITING'
            print(frameId,text)
            if text== 'Moving down':
              fadeInit=False
              if not scrollInit:
                scrollInit=True
                template= gray[400:700,10:1270]
                w, h = template.shape[::-1]
                print('saving ','/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg',frameId)
                #cv.imwrite('/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg', frame) - replace with actual connection to pipeline
                frame_list.append(gray)
                i += 1
              else:
                print(frameId)
                method = eval(meth)
                # Apply template Matching
                res = cv.matchTemplate(gray,template,method)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
                if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                  top_left = min_loc
                else:
                  top_left = max_loc
                print('top_left', top_left[1])
                if top_left[1]<=(700/16):
                  print('saving ','/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg',frameId)
                  #cv.imwrite('/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg', frame)- connect to actual pipeline
                  frame_list.append(gray)
                  template= gray[400:700,10:1270]
                  i += 1
            elif text == 'WAITING':
              scrollInit=False
              if not fadeInit:
                #frame1_clr=frame1
                frame1=gray
                #cv.imwrite('/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg', frame1)-connect to pipeline
                frame_list.append(frame1)
                print('saved first fade frame')
                fadeInit=True
                i += 1
              else:
                print('comparing ',frameId)
                #frame_clr=frame
                frame=gray
                ss=compare_images(frame1,frame)
                print('similarity',ss)
                if ss<0.99:
                  print('saving ',frameId)
                  #cv.imwrite('/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg', frame)-connect to pipeline
                  frame_list.append(frame)
                  i += 1
                  frame1=frame
                  dupCount=1
                elif ss>=0.99 and dupCount>0:
                  #cv.imwrite('/content/gdrive/MyDrive/EDGE_testing/attempt10/Frame'+str(i)+'.jpg', frame)-connect to pipeline
                  frame_list.append(frame)
                  i += 1
                  frame1=frame
                  dupCount-=1
                  

            else:
              scrollInit=False
              fadeInit=False

            print(frameId,text)

        k = cv.waitKey(1) & 0xff
        if k == ord('q'):
            break
      
        k = cv.waitKey(1) & 0xff
        if k == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
    return frame_list

#function for spelling correction
#pip install spellchecker
# from spellchecker import SpellChecker

# def correctSpelling(word,path_to_dict):
#   spell = SpellChecker(local_dictionary=path_to_dict) #can pass the gzipped file as well
#   return spell.correction(word)