# main.py

import cv2 as cv
import mediapipe
import pyautogui
from keyboard import Keyboard
from head_tilt_module import EyeTilt  # Importa la clase EyeTilt

# Initialize Face Mesh model
faceMesh = mediapipe.solutions.face_mesh.FaceMesh(refine_landmarks=True)
fr = cv.VideoCapture(0)

screenWidth, screenHeight = pyautogui.size()  # Get screen size

# Initialize the on-screen keyboard
keyboard = Keyboard()

# Inicializar el módulo de inclinación
eye_tilt = EyeTilt()  # Nueva línea

# Define the area where the icon is located (for mode change)
icon_x1, icon_y1 = 50, 50
icon_x2, icon_y2 = 150, 150  # Coordinates of the icon area

# Variables to store the position of the user's click
click_position = None
typed_text = ""

def mouse_callback(event, x, y, flags, param):
    global click_position, typed_text
    if event == cv.EVENT_LBUTTONDOWN:
        click_position = (x, y)
        typed_text = keyboard.type_text
        print(f"Clicked at position: {click_position}")
        print(f"Typed text: {typed_text}")

# Set the mouse callback function
cv.namedWindow('Image')
cv.setMouseCallback('Image', mouse_callback)

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

        # Detect if nose is over the keyboard mode toggle area
        nose_landmark = oneFacePoints[1]
        nose_x = int(nose_landmark.x * windowWidth)
        nose_y = int(nose_landmark.y * windowHeight)

        # Check if the nose is within the icon area to toggle the mode
        if icon_x1 < nose_x < icon_x2 and icon_y1 < nose_y < icon_y2:
            keyboard.toggle_mode()  # Switch between full keyboard and icon mode

        # Detectar inclinación de ojos y procesar la inclinación
        tilt = eye_tilt.detect_tilt(oneFacePoints)
        eye_tilt.process_tilt(tilt, keyboard)

    # Display the typed text at the clicked position
    if click_position and typed_text:
        cv.putText(image, typed_text, click_position, cv.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    cv.imshow('Image', image)

    # Exit the loop when 'Esc' key is pressed
    exitKey = cv.waitKey(1)
    if exitKey == 27:
        break

fr.release()
cv.destroyAllWindows()