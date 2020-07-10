import threading
from queue import Queue
import keyboard as kb

from servers import controller_server


class ControllerHandler:

    def __init__(self, host_ip, port_controller, run_controller_server):
        self.run_controller_server = run_controller_server

        # Creates and starts a TCP controller server(socket) to control what the motors do on the pi.
        # The server is ran on a thread to keep the connections seperated.
        self.server_controller = controller_server.ControllerServer(host_ip, port_controller)

        # Used to store/share the controller variable in a queue so the motors can be controlled from the main thread.
        self.controller = Queue()  # Can be -1, 0, 1, 2, or 3 -> do nothing, close connection, forward, left, right, signals respectively.
        self.controller.put(-1)

        if run_controller_server:
            self.controller_thread = threading.Thread(target=self.server_controller.start_server, name="controller_thread", args=((self.controller,)))
            self.controller_thread.start()


        # To get smooth keyboard input steering
        self.forward_pressed = False

        kb.on_release(self.on_key_release)


    def on_key_release(self, key):
        if   key.name == "left": self.controller.put(-1)
        elif key.name == "right": self.controller.put(-1)
        elif key.name == "up": self.controller.put(-1)


    def process_key_pressed(self, collect_data):
        # For controlling the car manually and to collect training data.

        if kb.is_pressed("down"):   # stop, do nothing.
            self.controller.put(-1) # Putting it in the queue for the controller server thread to be able to access it to send to the pi/motors.
        if kb.is_pressed("p"):      # close connection
            self.controller.put(0)

        # This if statement seperation/order is done for smooth steering using the keyboard.
        if kb.is_pressed("left"):     # steer left
            self.controller.put(2)
        elif kb.is_pressed("right"):  # steer right
            self.controller.put(3)
        elif kb.is_pressed("up"):     # go forward
            self.controller.put(1)


    def add_data_sample(self, frame, steering_dir):
        pass


    def save_collected_data(self):
        pass