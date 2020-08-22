import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg

import cv2
import time


class GUI:

    def __init__(self, c_ref):
        self.c_ref = c_ref  # Controller handler reference.

        self.canvas_size = (600, 600)
        self.canvas_bg = (255, 255, 255)

        pg.init()
        display = pg.display.set_mode(self.canvas_size)
        display.fill(self.canvas_bg)

        font = pg.font.Font(None, 32)
        text = font.render("Focus this window to use keyboard shortcuts", 1, (100, 100, 100))
        display.blit(text, (20, 20))
        pg.display.update()


    def process_key_pressed(self, frame=None):
        keys = pg.key.get_pressed()

        # This if statement separation/order is done for smooth steering using the keyboard.
        if keys[pg.K_LEFT]:      # steer left
            if self.c_ref.down_pressed:
                self.c_ref.controller.put(5)  # backwards left
            else:
                self.c_ref.controller.put(2)
                self.c_ref.add_data_sample(frame, 2)

        elif keys[pg.K_RIGHT]:   # steer right
            if self.c_ref.down_pressed:
                self.c_ref.controller.put(6)  # backwards right
            else:
                self.c_ref.controller.put(3)
                self.c_ref.add_data_sample(frame, 3)
                
        elif keys[pg.K_UP]:      # go forward
            self.c_ref.controller.put(1)
            self.c_ref.add_data_sample(frame, 1)

        elif keys[pg.K_DOWN]:
            self.c_ref.down_pressed = True
            self.c_ref.controller.put(4)  # reverse

        elif keys[pg.K_HASH]:
            self.c_ref.controller.put(-1) # stop, do nothing

        for event in pg.event.get():
            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT: self.c_ref.controller.put(-1)
                elif event.key == pg.K_RIGHT: self.c_ref.controller.put(-1)
                elif event.key == pg.K_UP: self.c_ref.controller.put(-1)
                elif event.key == pg.K_DOWN:
                    self.c_ref.down_pressed = False
                    self.c_ref.controller.put(-1)


                # On key release/key-up so nothing happens twice accidentally.
                if event.key == pg.K_s:  # Save all collected training data.
                    self.c_ref.save_collected_data()
                    print("Data collection - Training data SAVED")

                elif event.key == pg.K_p:  # Pause/unpause data collection
                    if self.c_ref.is_collecting_data:
                        self.c_ref.is_collecting_data = False
                        print("Data collection - Collection PAUSED")
                    else:
                        self.c_ref.is_collecting_data = True
                        print("Data collection - Collection STARTED")
    
                elif event.key == pg.K_r:
                    self.c_ref.reset_collected_data()
                    print("Data collection - Collected data RESET")
                
                elif event.key == pg.K_1:
                    if self.c_ref.is_collecting_data:
                        self.c_ref.rec_direction = 1
                        print("Data collection - Recording for forward(1) steering")
                    else:
                        self.c_ref.auto_direction = 1  # If not in collection mode, use 1,2,3 numbers to change model to use rather than changing recording direction.
                        print("Autonomous mode - Now using the forward model for driving.")

                elif event.key == pg.K_2:
                    if self.c_ref.is_collecting_data:
                        self.c_ref.rec_direction = 2
                        print("Data collection - Recording for left(2) steering")
                    else:
                        self.c_ref.auto_direction = 2
                        print("Autonomous mode - Now using the left model for driving.")

                elif event.key == pg.K_3:
                    if self.c_ref.is_collecting_data:
                        self.c_ref.rec_direction = 3
                        print("Data collection - Recording for right(3) steering")
                    else:
                        self.c_ref.auto_direction = 3
                        print("Autonomous mode - Now using the right model for driving.")

                elif event.key == pg.K_i:
                    self.c_ref.print_collection_info()

                elif event.key == pg.K_0:
                    self.c_ref.laps_done += 1
                    print("Data collection - lap added, done", self.c_ref.laps_done, "laps")
                elif event.key == pg.K_MINUS:
                    self.c_ref.laps_done = 0
                    print("Data collection - laps reset")

                elif event.key == pg.K_a:
                    self.c_ref.autonomous_mode = not self.c_ref.autonomous_mode
                    self.c_ref.controller.put(-1)
                    print(f"Autonomous mode - {self.c_ref.autonomous_mode}")

                elif event.key == pg.K_c:
                    if not os.path.exists("captured_images"): os.makedirs("captured_images")
                    file_name = int(time.time())
                    cv2.imwrite(f"captured_images/{file_name}.jpg", frame)