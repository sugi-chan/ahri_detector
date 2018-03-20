import cv2

dir = 'E:/LoL videos/ahri photos/ahri_3_class_photo/'
img_file = '2018-03-11 (427).png'

img = cv2.imread(dir+img_file,1)

label = 'THIS IS A TEST OF SKILLSHOT LOCATION'
cv2.putText(img, label, (0, 525),1,cv2.FONT_HERSHEY_PLAIN,
                        (0,255,0), 2)
label = 'THIS IS A TEST OF SKILLSHOT LOCATION'
cv2.putText(img, label, (0, 475),1,cv2.FONT_HERSHEY_PLAIN,
                        (0,255,0), 2)

cv2.imshow('image',img)
cv2.waitKey(0)
