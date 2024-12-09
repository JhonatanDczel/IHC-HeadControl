import cv2 as cv
import numpy as np

# Class to draw and interact with an on-screen keyboard
class Keyboard:
    def __init__(self):
        self.keyboard = np.zeros((1000, 1500, 3), np.uint8)
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.x_offset, self.y_offset = 50, 50  # Offsets for keys
        self.icon_offset = (50, 50)  # Icon position
        self.create_keyboard()
        self.is_full_keyboard = True  # Control to toggle between full keyboard and icon

    def create_keyboard(self):
        """Draw the full on-screen keyboard."""
        for i, letter_text in enumerate(self.letters):
            x = self.x_offset + (i % 10) * 120
            y = self.y_offset + (i // 10) * 120
            self.draw_key(x, y, letter_text)

    def draw_key(self, x, y, text):
        """Draw a key on the screen."""
        width = 100
        height = 100
        th = 3  # Border thickness

        # Draw the key
        cv.rectangle(self.keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 0, 0), th)

        # Add text to the key
        font_letter = cv.FONT_HERSHEY_PLAIN
        font_scale = 3
        font_th = 2
        text_size = cv.getTextSize(text, font_letter, font_scale, font_th)[0]
        width_text, height_text = text_size[0], text_size[1]

        # Center the text on the key
        text_x = int((width - width_text) / 2) + x
        text_y = int((height + height_text) / 2) + y
        cv.putText(self.keyboard, text, (text_x, text_y), font_letter, font_scale, (255, 0, 0), font_th)

    def detect_key_click(self, x, y):
        """Detect if a key is clicked based on the position of the nose."""
        if self.is_full_keyboard:
            for i, letter_text in enumerate(self.letters):
                key_x = self.x_offset + (i % 10) * 120
                key_y = self.y_offset + (i // 10) * 120
                width = 100
                height = 100
                if key_x < x < key_x + width and key_y < y < key_y + height:
                    return letter_text
        return None

    def get_keyboard_image(self):
        """Return the image of the keyboard or icon."""
        if self.is_full_keyboard:
            return self.keyboard  # Full keyboard image
        else:
            icon = np.zeros((200, 200, 3), np.uint8)
            cv.rectangle(icon, (50, 50), (150, 150), (255, 0, 0), -1)  # Draw a simple icon
            return icon

    def toggle_mode(self):
        """Toggle between full keyboard and icon mode."""
        self.is_full_keyboard = not self.is_full_keyboard
