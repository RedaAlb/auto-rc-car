from sign_detection.circle import Circle
import cv2
import numpy as np


class CircleDetector:
    # HoughCircles arguments. These were found by experimenting with different values.
    min_dist = 100  # Minimum distance between the centres of the detected circles.
    p1 = 386        # Method specific parameter
    p2 = 35         # Method specific parameter
    min_r = 7       # Minimum radius of circles to be detected.
    max_r = 26      # Maximum radius.
    dp = 0.1        # Inverse ratio of the accumulator resolution to the image resolution.


    def __init__(self, display_trackbars):
        self.display_trackbars = display_trackbars

        if self.display_trackbars:
            # Trackbars to "fine-tune" arguments for the HoughCircles function.
            cv2.namedWindow("trackbars")
            cv2.createTrackbar("min_dist", "trackbars", self.min_dist, 100, self.nothing)
            cv2.createTrackbar("p1", "trackbars", self.p1, 500, self.nothing)
            cv2.createTrackbar("p2", "trackbars", self.p2, 500, self.nothing)
            cv2.createTrackbar("min_r", "trackbars", self.min_r, 200, self.nothing)
            cv2.createTrackbar("max_r", "trackbars", self.max_r, 200, self.nothing)

    def nothing(self, x):  # For the trackbars.
        pass

    # Will find all the circles in the image and return 
    def find_circles(self, img):
        if self.display_trackbars:
            self.min_dist = cv2.getTrackbarPos("min_dist", "trackbars")
            self.p1 = cv2.getTrackbarPos("p1", "trackbars")
            self.p2 = cv2.getTrackbarPos("p2", "trackbars")
            self.min_r = cv2.getTrackbarPos("min_r", "trackbars")
            self.max_r = cv2.getTrackbarPos("max_r", "trackbars")


        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #img = cv2.GaussianBlur(img, (3, 3), cv2.BORDER_DEFAULT)

        # Excracting all the circles in the image.
        circles = cv2.HoughCircles(img,
                                   method=cv2.HOUGH_GRADIENT,
                                   dp=self.dp,
                                   minDist=self.min_dist,
                                   param1=self.p1,
                                   param2=self.p2,
                                   minRadius=self.min_r,
                                   maxRadius=self.max_r)


        
        
        # If no circles were found.
        if circles is None:
            return None

        # This will hold all the circles, each as a Circle object with its x, y (center), and radius.
        all_circles = []
        
        circles_rounded = np.uint16(np.around(circles))
        
        for circle in circles_rounded[0, :]:
            x = circle[0]
            y = circle[1]
            radius = circle[2]
            
            new_circle = Circle(x, y, radius)
            all_circles.append(new_circle)

        return all_circles
