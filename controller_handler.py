import threading
from queue import Queue

from servers import controller_server


class ControllerHandler:

    def __init__(self, host_ip, port_controller, run_controller_server):
        self.run_controller_server = run_controller_server

        # Creates and starts a TCP controller server(socket) to control what the motors do on the pi.
        # The server is ran on a thread to keep the connections seperated.
        self.server_controller = controller_server.ControllerServer(host_ip, port_controller)

        self.queue = Queue()  # Used to store/share the controller variable so the motors can be controlled from the main thread.

        if run_controller_server:
            self.controller_thread = threading.Thread(target=self.server_controller.start_server, name="controller_thread", args=((self.queue,)))
            self.controller_thread.start()
            

    def process_key_pressed(self, key_pressed):

        # TODO: Possibly make into a switch statement.

        if key_pressed == ord('s'):
            self.queue.put(-1)
        elif key_pressed == ord('w'):
            self.queue.put(1)
        elif key_pressed == ord('a'):
            self.queue.put(2)
        elif key_pressed == ord('d'):
            self.queue.put(3)
        elif key_pressed == ord('p'):
            self.queue.put(0)