import picamera
import struct
import sys
import time
import socket
import signal


pi_ip = "0.0.0.0"
pi_port = 5010

host_ip = "192.168.0.17"  #  desktop
# host_ip = "192.168.0.15"    #  laptop
host_port = 5000

host = (host_ip, host_port)


UDP_BYTE_LIMIT = 65507
SECONDS_TO_RECORD = 2000


FPS = 30
RESOLUTIONS = ["320x240", "640x480", "1280x720"]  # Please note for larger resolutions, splitting in half might then not be enough.
RES_INDEX = 0


# Creating the UDP socket and binding it locally to the pi.
cam_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cam_socket.bind((pi_ip, pi_port))


class CamHandler():
    def __init__(self, udp_byte_limit):
        self.udp_byte_limit = udp_byte_limit
        
    def write(self, img_bytes):
        img_num_bytes = len(img_bytes)
        # print(img_num_bytes)

        # Ensuring an image was successfully captured by the camera.
        if img_num_bytes > 0:
            try:
                # First sending the number of bytes to the host, so the host knows the size of the image to also check if
                # the frame is going to be split or not (if over the UDP_BYTE_LIMIT, the frame needs to be split in half).
                cam_socket.sendto(struct.pack("<L", img_num_bytes), host)
            except OSError as err:
                print("1  OSError, from image number of bytes:", str(err))
            

            # If the num of bytes exceeds the udp byte limit for a single packet, then split frame into two and send two seperate packets.
            if img_num_bytes >= self.udp_byte_limit:
                half_num_bytes = img_num_bytes // 2

                try:
                    cam_socket.sendto(img_bytes[:half_num_bytes], host)
                except OSError as err:
                    print("2  OSError, from half 1:", str(err))

                try:
                    cam_socket.sendto(img_bytes[half_num_bytes:], host)
                except OSError as err:
                    print("3  OSError, from half 2:", str(err))

            # Otherwise avoid unnecessary splitting and send the full frame as one packet.
            else:
                try:
                    cam_socket.sendto(img_bytes, host)
                except OSError as err:
                    print("4  OSError, from full frame:", str(err))
        
        # time.sleep(0.5)

    def flush(self):
        pass


# To handle CTRL+C exit
def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


try:
    cam_handler = CamHandler(UDP_BYTE_LIMIT)

    with picamera.PiCamera(resolution=RESOLUTIONS[RES_INDEX], framerate=FPS) as camera:
        print("PiCamera - Getting ready...")
        time.sleep(2)
        camera.rotation = 180
        #camera.color_effects = (128,128)
        camera.start_recording(cam_handler, format='mjpeg')
        print("PiCamera - Ready and is sending frames to the computer...")
        camera.wait_recording(SECONDS_TO_RECORD)
        camera.stop_recording()

finally:
    cam_socket.close()
    print("\nClient (camera) - connection closed")
