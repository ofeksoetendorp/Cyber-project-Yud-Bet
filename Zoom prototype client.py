import socket
import cv2


def get_video(vid):
    # define a video capture object

    ret, frame = vid.read()

    # Display the resulting frame
    return (cv2.flip(frame, 1)).tobytes()


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.0.0.13', 8485))  # IP could be 127.0.0.1 if local ip
    #Maybe use threading to send video and also receive messages at the same time
    vid = cv2.VideoCapture(0)
    while (True):

        # Capture the video frame
        # by frame

        client_socket.send(get_video(vid))  # Managed to mirror the video so it feels more natural

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    client_socket.close()

main()
