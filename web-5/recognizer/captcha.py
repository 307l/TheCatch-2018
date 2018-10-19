"""
To pass the CAPTCHA you need to identify "happy" smiley faces. Then lookup their R, G and B color channels. 
For each channel, xor together the values of all "happy" smileys and present the results to the CAPTCHA mechanism.

You only get one try per image. Submit your results via POST or GET (whichever you like). Submit the values in decimal. Use parameters names of r (for the red channel), g and b.

There is also a time limit present! You have up to 5 seconds to submit your answer.

http://challenges.thecatch.cz:10001/

> pip install opencv-python
> pip install cv2
> python captcha.py

"""
import requests, cv2, time

def rectContains(rect,pt):
    logic = rect[0] < pt[0] < rect[0]+rect[2] and rect[1] < pt[1] < rect[1]+rect[3]
    return logic

def gethappy(image):
    output = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #we need to convert the image to b&w
    im_bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 0)
   
    happy = {'r':[],'g':[],'b':[]}
   
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(im_bw, connectivity=8)

    gg = image.copy() #for debug only
    
    jj = 1
    # for every component in the output image
    for label in range(1,nlabels):
        
            # retrieving the width of the bounding box of the component
            width, height = stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT]
            # retrieving the leftmost and topmost coordinate of the bounding box of the component
            x, y = stats[label, cv2.CC_STAT_LEFT], stats[label, cv2.CC_STAT_TOP]
            
            #ignore object smaller than 40 pixels
            if min(width,height) < 40: continue
   
            #ignore object having less than three subcomponents
            subcomps = [i for i in range(nlabels) if rectContains((x,y,width,height),(stats[i, cv2.CC_STAT_LEFT],stats[i, cv2.CC_STAT_TOP]))]
            if len(subcomps) < 3: continue
    
            cv2.rectangle(gg,(x,y),(x+width,y+height),(255,255,255),1)

            circs, mouth = [], None
            for ll in subcomps:
                xx, yy = stats[ll, cv2.CC_STAT_LEFT], stats[ll, cv2.CC_STAT_TOP]
                ww, hh = stats[ll, cv2.CC_STAT_WIDTH], stats[ll, cv2.CC_STAT_HEIGHT]
                ctr = centroids[ll]

                #filter noise
                if max(ww, hh) < 3: continue


                #is it a circle? 
                # 1) width should be equal to height
                # 2)  (circle centroid should be equal to the bounding box centre), max difference is +- 1 pixel in each direction, i.e. sqrt(1+1)
                if cv2.norm(ctr, (xx+ww/2.0,yy+hh/2.0)) < 1.5 and abs(ww-hh) <= 2:
                    cv2.circle(gg,(xx+ww/2,yy+hh/2),ww/2,(255,255,255),2)
                    circs.append((ll,(xx+ww/2,yy+hh/2)))
                    continue
                #print ww,hh, (xx+ww/2.0,yy+hh/2.0), ctr, cv2.norm(ctr, (xx+ww/2.0,yy+hh/2.0))


                mouth = (ll, (xx+ww/2,yy+hh/2), (xx,yy,xx+ww,yy+hh), ll)
                cv2.circle(gg, (xx+ww/2,yy+hh/2), 5, (0,255,0),2)
              

            if len(circs) != 2 or not mouth:
                print width,height
                print 'circs',len(circs), 'mouth', mouth
                break
    
            ml = cv2.norm(centroids[mouth[3]], circs[0][1]) / width
            clr = image[circs[0][1][1],circs[0][1][0]]

            #the magic of happiness: the distance between centroid of mouth and an eye should be about 40%
            if ml>0.37: 
                happy['b'].append(clr[0])
                happy['g'].append(clr[1])
                happy['r'].append(clr[2])

                cv2.rectangle(gg,(x,y),(x+width,y+height),(0,0,255),2)

            jj += 1
    
    cv2.imshow('debug output',gg)
    return happy

r = requests.get('http://challenges.thecatch.cz:10001')
t = time.time()
assert r.headers['content-type'] == 'image/png'
open('smileys.png', 'wb').write(r.content)
image = cv2.imread('smileys.png')
h = gethappy(image)
if h:
   print 'solved in %.3f seconds' % (time.time() - t)
   res = {'r':reduce(lambda x,y: x ^ y, h['r']),'g':reduce(lambda x,y: x ^ y, h['g']),'b':reduce(lambda x,y: x ^ y, h['b'])}
   r = requests.post('http://challenges.thecatch.cz:10001', res, cookies=r.cookies)
   print r.text
   print 'total time: %.3f seconds' % (time.time() - t)

cv2.waitKey(0)
