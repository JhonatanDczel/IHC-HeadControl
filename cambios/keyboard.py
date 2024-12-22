# keyboard.py

import cv2 as cv
import numpy as np
import pyperclip  # Biblioteca para copiar al portapapeles

# Class to draw and interact with an on-screen keyboard
class Keyboard:
    def __init__(self):
        self.keyboard = np.zeros((350, 800, 3), np.uint8)  # Increased height to accommodate text
        self.first_col_index = [0, 10, 20, 30, 40, 50]
        self.second_col_index = [1, 11, 21, 31, 41, 51]
        self.third_col_index = [2, 12, 22, 32, 42, 52]
        self.fourth_col_index = [3, 13, 23, 33, 43, 53]
        self.fifth_col_index = [4, 14, 24, 34, 44, 54]
        self.sixth_col_index = [5, 15, 25, 35, 45, 55]
        self.seventh_col_index = [6, 16, 26, 36, 46, 56]
        self.eighth_col_index = [7, 17, 27, 37, 47, 57]
        self.ninth_col_index = [8, 18, 28, 38, 48, 58]
        self.tenth_col_index = [9, 19, 29, 39, 49, 59]
        self.key_set = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7", 7: "8", 8: "9", 9: "0",
                        10: "q", 11: "w", 12: "e", 13: "r", 14: "t", 15: "y", 16: "u", 17: "i", 18: "o", 19: "p",
                        20: "a", 21: "s", 22: "d", 23: "f", 24: "g", 25: "h", 26: "j", 27: "k", 28: "l", 29: ";",
                        30: "z", 31: "x", 32: "c", 33: "v", 34: "b", 35: "n", 36: "m", 37: "<", 38: ">", 39: "?",
                        40: "+", 41: "-", 42: ",", 43: ".", 44: "/", 45: "*", 46: "@", 47: " ", 48: "!", 49: "<-",
                        50: "%", 51: "$", 52: ":", 53: "&", 54: "(", 55: ")", 56: "=", 57: "_", 58: "'", 59: "#",
                        60: "COPY"}  # Added "COPY" key
        self.col = 0
        self.row = 0
        self.col_select = False
        self.frame_count_row = 0
        self.gaze_right_frame_count = 0
        self.gaze_left_frame_count = 0
        self.blink_count = 0
        self.blink_count_individual_key = 0
        self.type_text = ""  # To store the typed text
        self.font_letter = cv.FONT_HERSHEY_SIMPLEX

    def draw_keyboard(self, letter_index, letter, light):
        """Draw the keyboard layout."""
        x = (letter_index % 10) * 80
        y = (letter_index // 10) * 50
        if letter == "COPY":
            x = 720
            y = 300

        letter_thickness = 2
        key_space = 2
        font_scale = 1.5
        height = 50
        width = 80
        background_color = (173, 216, 230) if light else (135, 206, 250)
        text_color = (0, 0, 0)

        # Draw the key
        cv.rectangle(self.keyboard, (x + key_space, y + key_space), 
                     (x + width - key_space, y + height - key_space), 
                     background_color, -1)
        letter_size = cv.getTextSize(letter, self.font_letter, font_scale, letter_thickness)[0]
        letter_x = int((width - letter_size[0]) / 2) + x
        letter_y = int((height + letter_size[1]) / 2) + y
        cv.putText(self.keyboard, letter, (letter_x, letter_y), 
                   self.font_letter, font_scale, text_color, letter_thickness)

    def update_keyboard(self):
        """Update the keyboard layout based on gaze or blink detection."""
        if self.col_select:
            self.frame_count_row += 1
        if self.gaze_right_frame_count == 10:
            self.col += 1
            self.gaze_right_frame_count = 0
            if self.col == 10:
                self.col = 0
        if self.gaze_left_frame_count == 10:
            self.col -= 1
            self.gaze_left_frame_count = 0
            if self.col == -1:
                self.col = 9
        if self.frame_count_row == 10:
            self.row += 1
            if self.row == 6:
                self.row = 0
                self.col_select = False
            self.frame_count_row = 0
        self.keyboard[:, :, :] = (255, 255, 255)  # Clear the keyboard with white background
        col_index = self.get_col_index()
        if not self.col_select:
            for i in range(60):
                self.draw_keyboard(i, self.key_set[i], i in col_index)
        else:
            for i in range(60):
                self.draw_keyboard(i, self.key_set[i], i == col_index[self.row])
        # Draw the COPY key
        self.draw_keyboard(60, "COPY", False)

        # Draw the typed text at the bottom of the keyboard
        cv.rectangle(self.keyboard, (0, 300), (800, 350), (255, 255, 255), -1)
        cv.putText(self.keyboard, self.type_text, (10, 340), self.font_letter, 1, (0, 0, 0), 2)

    def get_col_index(self):
        """Get the column index based on the current column."""
        if self.col == 0:
            return self.first_col_index
        elif self.col == 1:
            return self.second_col_index
        elif self.col == 2:
            return self.third_col_index
        elif self.col == 3:
            return self.fourth_col_index
        elif self.col == 4:
            return self.fifth_col_index
        elif self.col == 5:
            return self.sixth_col_index
        elif self.col == 6:
            return self.seventh_col_index
        elif self.col == 7:
            return self.eighth_col_index
        elif self.col == 8:
            return self.ninth_col_index
        elif self.col == 9:
            return self.tenth_col_index

    def process_blink(self):
        """Process blink detection to type text."""
        self.blink_count += 1
        if self.col_select:
            self.blink_count_individual_key += 1
            self.frame_count_row -= 1
        if self.blink_count == 10:
            self.col_select = True
        if self.blink_count_individual_key == 10 and self.col_select:
            self.col_select = False
            key = self.key_set[self.get_col_index()[self.row]]
            if key == '<-':
                self.type_text = self.type_text[:-1]
            else:
                self.type_text += key
            self.blink_count_individual_key = 0
            self.row = 0

    def detect_key_click(self, x, y):
        """Detect if a key is clicked based on the position of the mouse click."""
        key_width, key_height = 80, 50
        col_index = self.get_col_index()
        for i in range(61):  # Include the COPY key
            key_x = (i % 10) * key_width
            key_y = (i // 10) * key_height
            if i == 60:  # Special case for the COPY key
                key_x = 720
                key_y = 300
            if key_x < x < key_x + key_width and key_y < y < key_y + key_height:
                key = self.key_set[i]
                if key == '<-':
                    self.type_text = self.type_text[:-1]
                elif key == "COPY":
                    self.copy_to_clipboard()
                else:
                    self.type_text += key
                return key
        return None

    def copy_to_clipboard(self):
        """Copy the typed text to the clipboard."""
        pyperclip.copy(self.type_text)

    def show_keyboard_window(self):
        """Show the keyboard in a separate window."""
        def mouse_callback(event, x, y, flags, param):
            if event == cv.EVENT_LBUTTONDOWN:
                self.detect_key_click(x, y)

        cv.namedWindow('Keyboard')
        cv.setMouseCallback('Keyboard', mouse_callback)
        while True:
            self.update_keyboard()
            keyboard_image = self.keyboard.copy()
            cv.imshow('Keyboard', keyboard_image)
            if cv.waitKey(100) == 27:  # Exit on 'Esc' key press
                self.copy_to_clipboard()  # Copy the text to the clipboard on exit
                break
        cv.destroyWindow('Keyboard')