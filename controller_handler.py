import threading
from queue import Queue
import pygame as pg
import sys

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

        # To get access to keyboard key press and key release for data collection.
        pg.init()
        display = pg.display.set_mode((400, 400))
        display.fill((255, 255, 255))

        # To get smooth keyboard input steering
        self.forward_pressed = False
            

    def process_key_pressed(self, collect_data):

        # For controlling car manually and to collect training data.
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:     # stop
                    self.queue.put(-1)  # Putting it in the queue for the controller thread to be able to access it to send to the pi/motors.

                elif event.key == pg.K_UP:     # forward
                    self.queue.put(1)
                    self.forward_pressed = True

                elif event.key == pg.K_LEFT:   # left
                    self.queue.put(2)

                elif event.key == pg.K_RIGHT:  # right
                    self.queue.put(3)

                elif event.key == pg.K_p:      # close controller connection
                    self.queue.put(0)
            
            elif event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.queue.put(-1)
                    self.forward_pressed = False

                elif event.key == pg.K_LEFT:
                    if self.forward_pressed: self.queue.put(1)
                    else: self.queue.put(-1)

                elif event.key == pg.K_RIGHT:
                    if self.forward_pressed: self.queue.put(1)
                    else: self.queue.put(-1)

    

    def save_collected_data(self):
        pass

    def close_controller_window(self):
        pg.quit()