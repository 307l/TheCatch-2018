import cv2
image = cv2.imread('message.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

assert len(gray[0,:]) % 7 == 0

v = 0
s = ''
for i,ch in enumerate(gray[0,:]):
    v = (v << 1) | (~ch&1)
    if i%7==6 and i:
        s += chr(v)
        v = 0

print s
