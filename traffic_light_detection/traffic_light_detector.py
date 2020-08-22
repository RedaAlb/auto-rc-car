import numpy as np
import cv2

class TrafficLightDetector:
    
    font = cv2.FONT_HERSHEY_DUPLEX
    tl_cascade = cv2.CascadeClassifier("traffic_light_detection/tl_cascade.xml")  # tl -> traffic light.

    def detect_traffic_light(self, frame):

        # Using the trained Haar cascade detector to detect the traffic light in the frame.
        tl = self.tl_cascade.detectMultiScale(frame, 1.01, 5)
    
        detected_light = 0     # This will be 0 if no traffic light was detected, 1 if red/yellow, 2 if green.
        dist_to_edge = 0       # This will hold distance from the traffic light to the closest edge of the frame.

        if len(tl) is not 0:  # If a traffic light was detected.
            x, y = tl[0][0], tl[0][1]
            w, h = tl[0][2], tl[0][3]

            rect_mid = (x + (w//2), y + (h//2))  # Centre of traffic light.


            # To detect which light (red, yellow or green) is displayed on traffic light, the tl bounding box is cut vertically in two sections, where one
            # half includes the red&yellow lights, and the other the green light. Then two methods are tried to determine which light the tl is on.
            # Note: I am considering a yellow light as a red light, hence why it is in the red section, because the car needs to stop in yellow light as well.
            roi = frame[y:y+h, x:x+w, :]  # Region of interest (roi)

            # 1.5 thirds of the height to include the red and yellow lights. Not exactly 2/3 as the detector tends to include more of the bottom section.
            top_half_height = int(1.5 * (roi.shape[0] // 3))
            top_half = roi[0:top_half_height, :, :]
            
            bottom_half = roi[top_half_height:, :, :]

            # Method 1: Checking average pixel intensity in each half.
            # if np.average(top_half) > np.average(bottom_half):
            #     frame = cv2.putText(frame, "Red", (rect_mid[0] - w//2, y - 30), self.font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            #     detected_light = 1  # Red light detected
            # else:
            #     frame = cv2.putText(frame, "Green", (rect_mid[0] - w//2, y - 30), self.font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            #     detected_light = 2  # Green light detected


            # Method 2: Checking brightest pixel in each half.
            top_half_brightest = np.average(top_half.max(axis=(0, 1)))
            bottom_half_brightest = np.average(bottom_half.max(axis=(0, 1)))

            if top_half_brightest > bottom_half_brightest:
                frame = cv2.putText(frame, "Red", (rect_mid[0] - w//2, y - 30), self.font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                detected_light = 1  # Red light detected
            else:
                frame = cv2.putText(frame, "Green", (rect_mid[0] - w//2, y - 30), self.font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                detected_light = 2  # Green light detected
                




            # Displaying traffic light bounding box and calculating the distance from centre of traffic light to the closest vertical edge of frame.
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Bounding box.

            frame_width = frame.shape[1]
            dist_to_edge = (frame_width // 2) - abs((frame_width//2) - rect_mid[0])

            # Displaying the distance and drawing the line to represent the distance depending on which side the tl is on.
            if rect_mid[0] < frame_width//2:  # Left side.
                edge_of_screen = (0, y + (h//2))
            else:
                edge_of_screen = (frame_width, y + (h//2))

            frame = cv2.line(frame, rect_mid, edge_of_screen, (0, 255, 0), 2)
            frame = cv2.putText(frame, str(dist_to_edge), (rect_mid[0] - w//2, y - 10), self.font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)



            # If a traffic light is detected, it is covered by a black box so when the image is used to detect signs, it is not confused by
            # the traffic lights. Note: After some tweaking to the sign detector, this was no longer needed.
            # frame[y:y+h, x:x+w, :] = 0
        
        

        # Returns the image, the light detected, which will be 1 for red and 2 for green. Otherwise 0 if no light is detected,
        # and also the distance from the traffic light to the corresponding edge.
        return frame, detected_light, dist_to_edge
