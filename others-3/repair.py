#pip install pyzbar
import cv2
im = cv2.imread('Pixels.png')
w,h,clrs = im.shape
im = im[9:h-10, 7:w-12] #crop
w,h,clrs = im.shape
sz = w/25.0

def finder(x,y,r=0,s=0):
    W,B = (255,255,255),(0,0,0)
    def i(a,b): return int(a),int(b)
    cv2.rectangle(im,i(x*sz,y*sz),i((x+8)*sz,(y+8)*sz),W, cv2.FILLED)
    cv2.rectangle(im,i((x+r)*sz,(y+s)*sz),i((x+7+r)*sz,(y+7+s)*sz),B, cv2.FILLED)
    cv2.rectangle(im,i((x+r+1)*sz,(y+1+s)*sz),i((x+6+r)*sz,(y+6+s)*sz),W, cv2.FILLED)
    cv2.rectangle(im,i((x+r+2)*sz,(y+2+s)*sz),i((x+5+r)*sz,(y+5+s)*sz),B, cv2.FILLED)

finder(0,0)
finder(25-8,0,1)
finder(0,25-8,0,1)

#im = cv2.copyMakeBorder(im,50,50,50,50,cv2.BORDER_CONSTANT,value=(255,255,255)) #make border

cv2.imshow('QR repaired',im)
cv2.waitKey(0)

cv2.imwrite('qr.png',im)


#not working
#from pyzbar.pyzbar import decode
#from pyzbar.pyzbar import ZBarSymbol
#print decode(im, symbols=[ZBarSymbol.QRCODE])

import zxing
reader = zxing.BarCodeReader()
print reader.decode("qr.png")
