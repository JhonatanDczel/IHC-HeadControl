import cv2 as cv
import mediapipe
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk  # Import Pillow for image conversion
from threading import Thread

class EyeMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Head Control")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(root, width=800, height=400)
        self.canvas.pack()

        self.status_label = tk.Label(root, text="Estado: Iniciando...", font=("Helvetica", 14))
        self.status_label.pack(pady=10)

        self.faceMesh = mediapipe.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.fr = cv.VideoCapture(0)

        self.screenWidth, self.screenHeight = pyautogui.size()

        self.action_area = {
            "left": 0.3,  # 30% de la pantalla desde la izquierda
            "right": 0.7,  # 70% de la pantalla desde la izquierda
            "top": 0.3,  # 30% de la pantalla desde la parte superior
            "bottom": 0.7,  # 70% de la pantalla desde la parte superior
        }

        self.update_frame()

    def map_nose_to_cursor(self, nose_x, nose_y, action_area, screenWidth, screenHeight):
        # Normaliza la posición de la nariz dentro del rectángulo de acción
        normalized_x = (nose_x - action_area["left"]) / (action_area["right"] - action_area["left"])
        normalized_y = (nose_y - action_area["top"]) / (action_area["bottom"] - action_area["top"])

        # Convierte la posición normalizada a coordenadas de pantalla
        cursor_x = int(normalized_x * screenWidth)
        cursor_y = int(normalized_y * screenHeight)

        # Asegúrate de que el cursor no salga de los límites de la pantalla
        cursor_x = max(0, min(cursor_x, screenWidth))
        cursor_y = max(0, min(cursor_y, screenHeight))

        return cursor_x, cursor_y

    def update_frame(self):
        ret, image = self.fr.read()
        if not ret:
            print("No se pudo capturar la imagen")
            self.status_label.config(text="Estado: No se pudo capturar la imagen")
            self.root.after(10, self.update_frame)
            return

        image = cv.flip(image, 1)
        windowHieght, windowWidth, _ = image.shape

        rgbImage = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        processImage = self.faceMesh.process(rgbImage)
        allFaces = processImage.multi_face_landmarks

        if allFaces:
            oneFacePoints = allFaces[0].landmark

            nose_landmark = oneFacePoints[1]
            nose_x = int(nose_landmark.x * windowWidth)
            nose_y = int(nose_landmark.y * windowHieght)

            if (self.action_area["left"] * windowWidth < nose_x < self.action_area["right"] * windowWidth and
                self.action_area["top"] * windowHieght < nose_y < self.action_area["bottom"] * windowHieght):
                mouseX, mouseY = self.map_nose_to_cursor(nose_x, nose_y, windowWidth, windowHieght)
                smoothed_x, smoothed_y = self.smooth_movement(mouseX, mouseY)
                pyautogui.moveTo(smoothed_x, smoothed_y)

            cv.rectangle(
                image,
                (int(self.action_area["left"] * windowWidth), int(self.action_area["top"] * windowHieght)),
                (int(self.action_area["right"] * windowWidth), int(self.action_area["bottom"] * windowHieght)),
                (255, 0, 0), 2
            )

            cv.circle(image, (nose_x, nose_y), 5, (0, 255, 255), -1)


            rightEye = [oneFacePoints[374], oneFacePoints[386]]
            for id, landMark in enumerate(rightEye):
                x = int(landMark.x * windowWidth)
                y = int(landMark.y * windowHieght)

                if id == 1:
                    mouseX = int(self.screenWidth / windowWidth * x)
                    mouseY = int(self.screenHeight / windowHieght * y)
                    pyautogui.moveTo(mouseX, mouseY)

                cv.circle(image, (x, y), 2, (0, 255, 0))

            leftEye = [oneFacePoints[145], oneFacePoints[159]]
            for landMark in leftEye:
                x = int(landMark.x * windowWidth)
                y = int(landMark.y * windowHieght)
                cv.circle(image, (x, y), 2, (0, 0, 255))



            rightEyeClosed = (rightEye[0].y - rightEye[1].y) < 0.01
            leftEyeClosed = (leftEye[0].y - leftEye[1].y) < 0.01

            if rightEyeClosed and leftEyeClosed:
                print("Both Eyes Closed -> Scrolling down")
                self.status_label.config(text="Estado: Ambos Ojos Cerrados -> Scroll abajo")
                pyautogui.scroll(-100)
            elif rightEyeClosed:
                print("Right Eye Closed -> Mouse clicked")
                self.status_label.config(text="Estado: Ojo Derecho Cerrado -> Click")
                pyautogui.rightClick()
                pyautogui.sleep(1)
            elif leftEyeClosed:
                print("Left Eye Closed -> Mouse clicked")
                self.status_label.config(text="Estado: Ojo Izquierdo Cerrado -> Click")
                pyautogui.click()
                pyautogui.sleep(1)
            else:
                self.status_label.config(text="Estado: Ojos abiertos")

        self.display_image(image)
        self.root.after(10, self.update_frame)

    def display_image(self, image):
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image = cv.resize(image, (800, 400))
        image = Image.fromarray(image)  # Convert OpenCV image to PIL image
        photo = ImageTk.PhotoImage(image)  # Convert PIL image to ImageTk.PhotoImage
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo  # Keep a reference to avoid garbage collection
        self.root.update_idletasks()

    def on_closing(self):
        self.fr.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EyeMouseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
