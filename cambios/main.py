import cv2 as cv
import mediapipe
import pyautogui
from keyboard import Keyboard

# Initialize Face Mesh model
faceMesh = mediapipe.solutions.face_mesh.FaceMesh(refine_landmarks=True)
fr = cv.VideoCapture(0)

screenWidth, screenHeight = pyautogui.size()  # Get screen size

# Initialize the on-screen keyboard
keyboard = Keyboard()

# Define the area where the icon is located (for mode change)
icon_x1, icon_y1 = 50, 50
icon_x2, icon_y2 = 150, 150  # Coordinates of the icon area

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

        # Display the keyboard or icon on the screen
        keyboard_image = keyboard.get_keyboard_image()

        # Redimensionar la imagen del teclado para que coincida con el tamaño de la imagen de la cámara
        keyboard_image = cv.resize(keyboard_image, (image.shape[1], image.shape[0]))

        image = cv.addWeighted(image, 0.7, keyboard_image, 0.3, 0)

    cv.imshow('Image', image)

    # Exit the loop when 'Esc' key is pressed
    exitKey = cv.waitKey(1)
    if exitKey == 27:
        break

fr.release()
cv.destroyAllWindows()
