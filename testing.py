# import the opencv library
import cv2
import numpy
import sys
# define a video capture object
"""
vid = cv2.VideoCapture(0)
ret, frame = vid.read()
numpy.set_printoptions(threshold=sys.maxsize)
print(frame.shape)
print(frame.dtype)
#print(frame)
xBytes = frame.tobytes()
#x = numpy.array([[1.0,1.1,1.2,1.3],[2.0,2.1,2.2,2.3],[3.0,3.1,3.2,3.3]],numpy.float64)
#array([[1. , 1.1, 1.2, 1.3],
#       [2. , 2.1, 2.2, 2.3],
#       [3. , 3.1, 3.2, 3.3]])
#print(x)
#xBytes = x.tobytes()
#b'\x00\x00\x00\x00\x00\x00\xf0?\x9a\x99\x99\x99\x99\x99\xf1?333333\xf3?\xcd\xcc\xcc\xcc\xcc\xcc\xf4?\x00\x00\x00\x00\x00\x00\x00@\xcd\xcc\xcc\xcc\xcc\xcc\x00@\x9a\x99\x99\x99\x99\x99\x01@ffffff\x02@\x00\x00\x00\x00\x00\x00\x08@\xcd\xcc\xcc\xcc\xcc\xcc\x08@\x9a\x99\x99\x99\x99\x99\t@ffffff\n@'

newX = numpy.ndarray(frame.shape,frame.dtype,xBytes)
print(numpy.array_equal(frame,newX))
"""
vid = cv2.VideoCapture(0)

while (True):

    # Capture the video frame 
    # by frame 
    ret, frame = vid.read()
    numpy.set_printoptions(threshold=sys.maxsize)
    print(frame.shape)
    print(frame.dtype)
    #print(frame)
    xBytes = frame.tobytes()
    print(len(xBytes))
    #x = numpy.array([[1.0,1.1,1.2,1.3],[2.0,2.1,2.2,2.3],[3.0,3.1,3.2,3.3]],numpy.float64)
    #array([[1. , 1.1, 1.2, 1.3],
    #       [2. , 2.1, 2.2, 2.3],
    #       [3. , 3.1, 3.2, 3.3]])
    #print(x)
    #xBytes = x.tobytes()
    #b'\x00\x00\x00\x00\x00\x00\xf0?\x9a\x99\x99\x99\x99\x99\xf1?333333\xf3?\xcd\xcc\xcc\xcc\xcc\xcc\xf4?\x00\x00\x00\x00\x00\x00\x00@\xcd\xcc\xcc\xcc\xcc\xcc\x00@\x9a\x99\x99\x99\x99\x99\x01@ffffff\x02@\x00\x00\x00\x00\x00\x00\x08@\xcd\xcc\xcc\xcc\xcc\xcc\x08@\x9a\x99\x99\x99\x99\x99\t@ffffff\n@'

    newX = numpy.ndarray(frame.shape,frame.dtype,xBytes)
    print(numpy.array_equal(frame,newX))
    # Display the resulting frame
    cv2.imshow('frame', numpy.flip(newX,1)) #Managed to mirror the video so it feels more natural

    # the 'q' button is set as the 
    # quitting button you may use any 
    # desired button of your choice 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object 
vid.release()
# Destroy all the windows 
cv2.destroyAllWindows()