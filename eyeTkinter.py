import cv2 as cv
import mediapipe
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk  # Import Pillow for image conversion

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

        # Define rectángulo de acción
        self.action_area = {
            "left": 0.3,  # 30% desde la izquierda
            "right": 0.7,  # 70% desde la izquierda
            "top": 0.3,  # 30% desde arriba
            "bottom": 0.7,  # 70% desde abajo
        }

        # Variables de suavizado
        self.smoothing_factor = 0.7
        self.previous_mouse_x = 0
        self.previous_mouse_y = 0

        self.update_frame()

    def map_nose_to_cursor(self, nose_x, nose_y, windowWidth, windowHeight):
        """Mapea la posición de la nariz dentro del rectángulo al área de la pantalla."""
        # Normalización de las coordenadas dentro del rectángulo
        normalized_x = (nose_x - self.action_area["left"] * windowWidth) / (
            (self.action_area["right"] - self.action_area["left"]) * windowWidth)
        normalized_y = (nose_y - self.action_area["top"] * windowHeight) / (
            (self.action_area["bottom"] - self.action_area["top"]) * windowHeight)

        # Convierte a coordenadas de pantalla
        cursor_x = int(normalized_x * self.screenWidth)
        cursor_y = int(normalized_y * self.screenHeight)

        # Asegúrate de que no salga de los límites de la pantalla
        cursor_x = max(0, min(cursor_x, self.screenWidth))
        cursor_y = max(0, min(cursor_y, self.screenHeight))

        return cursor_x, cursor_y

    def smooth_movement(self, mouseX, mouseY):
        """Aplica suavizado exponencial al movimiento."""
        smoothed_x = int(self.smoothing_factor * self.previous_mouse_x + (1 - self.smoothing_factor) * mouseX)
        smoothed_y = int(self.smoothing_factor * self.previous_mouse_y + (1 - self.smoothing_factor) * mouseY)

        self.previous_mouse_x = smoothed_x
        self.previous_mouse_y = smoothed_y

        return smoothed_x, smoothed_y

    def update_frame(self):
        """Actualiza el frame de video y procesa los puntos faciales."""
        ret, image = self.fr.read()
        if not ret:
            self.status_label.config(text="Estado: No se pudo capturar la imagen")
            self.root.after(10, self.update_frame)
            return

        image = cv.flip(image, 1)
        windowHeight, windowWidth, _ = image.shape

        rgbImage = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        processImage = self.faceMesh.process(rgbImage)
        allFaces = processImage.multi_face_landmarks

        if allFaces:
            oneFacePoints = allFaces[0].landmark

            # Detección de la nariz
            nose_landmark = oneFacePoints[1]
            nose_x = int(nose_landmark.x * windowWidth)
            nose_y = int(nose_landmark.y * windowHeight)

            # Si la nariz está dentro del área de acción, mueve el cursor
            if (self.action_area["left"] * windowWidth < nose_x < self.action_area["right"] * windowWidth and
                self.action_area["top"] * windowHeight < nose_y < self.action_area["bottom"] * windowHeight):
                mouseX, mouseY = self.map_nose_to_cursor(nose_x, nose_y, windowWidth, windowHeight)
                smoothed_x, smoothed_y = self.smooth_movement(mouseX, mouseY)
                pyautogui.moveTo(smoothed_x, smoothed_y)

            # Detección de los ojos
            rightEye = [oneFacePoints[374], oneFacePoints[386]]
            leftEye = [oneFacePoints[145], oneFacePoints[159]]

            rightEyeClosed = abs(rightEye[0].y - rightEye[1].y) < 0.01
            leftEyeClosed = abs(leftEye[0].y - leftEye[1].y) < 0.01

            if rightEyeClosed and leftEyeClosed:
                self.status_label.config(text="Estado: Ambos ojos cerrados -> Scroll hacia abajo")
                pyautogui.scroll(-100)
            elif rightEyeClosed:
                self.status_label.config(text="Estado: Ojo derecho cerrado -> Clic derecho")
                pyautogui.rightClick()
            elif leftEyeClosed:
                self.status_label.config(text="Estado: Ojo izquierdo cerrado -> Clic izquierdo")
                pyautogui.click()
            else:
                self.status_label.config(text="Estado: Ojos abiertos")

            # Visualización de la nariz y los ojos
            for eye in [rightEye, leftEye]:
                for landmark in eye:
                    x = int(landmark.x * windowWidth)
                    y = int(landmark.y * windowHeight)
                    cv.circle(image, (x, y), 3, (0, 255, 0), -1)
            cv.circle(image, (nose_x, nose_y), 5, (0, 255, 255), -1)

            # Dibuja el rectángulo de acción
            cv.rectangle(
                image,
                (int(self.action_area["left"] * windowWidth), int(self.action_area["top"] * windowHeight)),
                (int(self.action_area["right"] * windowWidth), int(self.action_area["bottom"] * windowHeight)),
                (255, 0, 0), 2
            )

        self.display_image(image)
        self.root.after(10, self.update_frame)

    def display_image(self, image):
        """Muestra el video en la interfaz gráfica."""
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image = cv.resize(image, (800, 400))
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo
        self.root.update_idletasks()

    def on_closing(self):
        """Libera recursos al cerrar la aplicación."""
        self.fr.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EyeMouseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
