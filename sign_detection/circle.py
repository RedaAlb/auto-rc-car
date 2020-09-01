import cv2

class Circle:

    FONT = cv2.FONT_HERSHEY_DUPLEX

    RED_COLOUR = (0, 0, 255)
    GREEN_COLOUR = (0, 255, 0)

    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    # Getting the rectangle coordinates that the circle makes (is inside of, from edge to edge).
    def get_rect_coords(self):

        padding = self.r // 2

        top_l_corner = (int(self.x - self.r) - padding, int(self.y - self.r) - padding)
        bottom_r_corner = (int(self.x + self.r + padding), int(self.y + self.r) + padding)

        return top_l_corner, bottom_r_corner

    # To draw the sign bounding box.
    def draw_sign_rect(self, img, top_l_corner, bottom_r_corner):
        img = cv2.rectangle(img, top_l_corner, bottom_r_corner, self.GREEN_COLOUR, 2)
        return img

    # Get the distance of the sign detected from its centre to the closest horizontal edge of the frame.
    def get_dist_to_edge(self, frame_width):

        d_to_edge = 0

        if self.x >= frame_width // 2:
            d_to_edge = frame_width - self.x
        else:
            d_to_edge = self.x

        return d_to_edge

    # To draw the line from the centre of the sign to the closest edge of the frame.
    def draw_line_to_edge(self, img, sign_dist):
        x = self.x
        y = self.y
        text_pos = (x, y)

        img_width = img.shape[1]

        if x >= img_width // 2:
            img = cv2.line(img, (x, y), (img_width, y), self.GREEN_COLOUR, 3)
            text_pos = (x + int(sign_dist / 2), y - 10)
        else:
            img = cv2.line(img, (0, y), (x, y), self.GREEN_COLOUR, 3)
            text_pos = (int(x/2), y - 10)

        img = cv2.putText(img, str(sign_dist), text_pos, self.FONT, 0.5, self.GREEN_COLOUR, 1, cv2.LINE_AA)

        return img

    def draw_circle(self, img):
        img = cv2.circle(img, (self.x, self.y), self.r, self.RED_COLOUR, 2)
        return img

    def draw_sign_name(self, img, sign_name, top_l_corner):
        img = cv2.putText(img, sign_name, (top_l_corner[0]-20, top_l_corner[1]-10), self.FONT, 0.5, self.GREEN_COLOUR, 1, cv2.LINE_AA)
        return img

    # Displaying sign bounding box, the line from centre of sign to the edge of the screen, sign circle, and the sign name.
    def draw_sign_info(self, img, top_l_corner, bottom_r_corner, sign_dist, sign_name):

        img = self.draw_sign_rect(img, top_l_corner, bottom_r_corner)
        img = self.draw_line_to_edge(img, sign_dist)
        img = self.draw_circle(img)
        img = self.draw_sign_name(img, sign_name, top_l_corner)

        return img

