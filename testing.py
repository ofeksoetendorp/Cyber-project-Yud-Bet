import cv2
import numpy as np
import sys
import socket
# define a video capture object

file_path = r"captured_picture.jpg"

def get_image_size_in_memory_len(image_path):
    # Read the image
    image_bytes = open(file_path,"rb").read()

    print(f"The size of the image in memory is approximately {type(image_bytes)}  bytes.")
    my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    my_socket.connect(("10.0.0.17",8485))
    my_socket.send(image_bytes)

# Example usage
get_image_size_in_memory_len(r"captured_picture.jpg")
read_photo = open(file_path,"rb").read()
print(len(read_photo))
"""
def take_picture(file_path='captured_picture.jpg'):
    # Open a connection to the camera (0 represents the default camera)
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Capture a single frame
    ret, frame = cap.read()

    # Check if the frame is captured successfully
    if not ret:
        print("Error: Could not capture frame.")
        cap.release()  # Release the camera
        return

    # Save the captured frame to a file
    cv2.imwrite(file_path, frame)

    # Release the camera
    cap.release()

    print(f"Picture captured and saved to {file_path}.")

# Example usage
take_picture('captured_picture.jpg')
picture = open("captured_picture.jpg")
image = cv2.imread("captured_picture.jpg")
cv2.imshow("Image",image)
cv2.waitKey(0)
cv2.destroyAllWindows()

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
cv2.destroyAllWindows()"""
