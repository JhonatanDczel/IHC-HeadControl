import cv2 as cv
import mediapipe
import pyautogui
import numpy as np

# Class to draw and interact with an on-screen keyboard
class Keyboard:
    def __init__(self):
        self.keyboard = np.zeros((1000, 1500, 3), np.uint8)
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.x_offset, self.y_offset = 50, 50  # Offsets for keys
        self.create_keyboard()

    def create_keyboard(self):
        """Draw the on-screen keyboard."""
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
        for i, letter_text in enumerate(self.letters):
            key_x = self.x_offset + (i % 10) * 120
            key_y = self.y_offset + (i // 10) * 120
            width = 100
            height = 100
            if key_x < x < key_x + width and key_y < y < key_y + height:
                return letter_text
        return None

    def get_keyboard_image(self):
        """Return the image of the keyboard."""
        return self.keyboard


# Initialize Face Mesh model
faceMesh = mediapipe.solutions.face_mesh.FaceMesh(refine_landmarks=True)
fr = cv.VideoCapture(0)

screenWidth, screenHeight = pyautogui.size()  # Get screen size

# Initialize the on-screen keyboard
keyboard = Keyboard()

while True:
    _, image = fr.read()
    image = cv.flip(image, 1)

    windowHeight, windowWidth, _ = image.shape

    rgbImage = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    processImage = faceMesh.process(rgbImage)
    allFaces = processImage.multi_face_landmarks

    if allFaces:
        oneFacePoints = allFaces[0].landmark

        # Right eye detection
        rightEye = [oneFacePoints[374], oneFacePoints[386]]
        for id, landMark in enumerate(rightEye):
            x = int(landMark.x * windowWidth)
            y = int(landMark.y * windowHeight)

            if id == 1:
                mouseX = int(screenWidth / windowWidth * x)
                mouseY = int(screenHeight / windowHeight * y)

                pyautogui.moveTo(mouseX, mouseY)

            cv.circle(image, (x, y), 2, (0, 255, 0))

        # Left eye detection
        leftEye = [oneFacePoints[145], oneFacePoints[159]]
        for landMark in leftEye:
            x = int(landMark.x * windowWidth)
            y = int(landMark.y * windowHeight)
            cv.circle(image, (x, y), 2, (0, 0, 255))

        # Check if eyes are closed
        rightEyeClosed = (rightEye[0].y - rightEye[1].y) < 0.01
        leftEyeClosed = (leftEye[0].y - leftEye[1].y) < 0.01

        if rightEyeClosed and leftEyeClosed:
            pyautogui.scroll(-100)

        elif rightEyeClosed:
            pyautogui.rightClick()

        elif leftEyeClosed:
            pyautogui.click()

        # Detect if nose is over a key
        nose_landmark = oneFacePoints[1]
        nose_x = int(nose_landmark.x * windowWidth)
        nose_y = int(nose_landmark.y * windowHeight)

        letter = keyboard.detect_key_click(nose_x, nose_y)
        if letter:
            pyautogui.typewrite(letter)

        # Resize the keyboard image to match the camera frame dimensions
        keyboard_image = keyboard.get_keyboard_image()
        keyboard_image_resized = cv.resize(keyboard_image, (image.shape[1], image.shape[0]))

        # Combine the images after resizing the keyboard image
        image = cv.addWeighted(image, 0.7, keyboard_image_resized, 0.3, 0)

    cv.imshow('Image', image)

    # Exit the loop when 'Esc' key is pressed
    exitKey = cv.waitKey(1)
    if exitKey == 27:
        break

fr.release()
cv.destroyAllWindows()
