import time
import threading
import pyautogui
import webbrowser  # Para abrir el navegador predeterminado

class EyeTilt:
    def __init__(self, tilt_threshold=0.02, hold_time=3.0, cooldown_time=3.0):
        """
        Inicializa el detector de inclinación basado en la posición de los ojos.
        :param tilt_threshold: Umbral para inclinación.
        :param hold_time: Tiempo necesario para confirmar inclinación sostenida.
        :param cooldown_time: Tiempo de espera entre acciones.
        """
        self.tilt_threshold = tilt_threshold  # Umbral de diferencia vertical de los ojos
        self.hold_time = hold_time  # Tiempo para inclinación sostenida
        self.cooldown_time = cooldown_time  # Tiempo de espera entre comandos
        self.tilt_timer = None  # Temporizador para detectar sostenimiento
        self.previous_tilt = None  # Última inclinación detectada
        self.last_action_time = 0  # Registro del tiempo de la última acción

    def detect_tilt(self, landmarks):
        """
        Detecta inclinación usando la diferencia vertical entre los ojos.
        """
        # Coordenadas Y de los ojos
        left_eye_top = landmarks[145].y
        left_eye_bottom = landmarks[159].y
        right_eye_top = landmarks[374].y
        right_eye_bottom = landmarks[386].y

        # Promedio de posiciones Y para los ojos
        left_eye_y = (left_eye_top + left_eye_bottom) / 2
        right_eye_y = (right_eye_top + right_eye_bottom) / 2

        # Calcular la diferencia entre ojos
        eye_difference = left_eye_y - right_eye_y

        # Detección de inclinación
        if eye_difference > self.tilt_threshold:  # Ojo izquierdo más alto
            return "left"
        elif eye_difference < -self.tilt_threshold:  # Ojo derecho más alto
            return "right"
        return None

    def execute_action(self, action):
        """Ejecuta una acción específica en un hilo separado."""
        def action_thread():
            if action == "task_browser":
                print("Inclinación izquierda sostenida: Abriendo navegador de Internet...")
                webbrowser.open("https://www.google.com")  # Abre navegador predeterminado
            elif action == "task_explorer":
                print("Inclinación derecha sostenida: Activando Explorador de archivos...")
                pyautogui.hotkey("win", "e")

        threading.Thread(target=action_thread).start()

    def process_tilt(self, tilt):
        """
        Procesa la inclinación y ejecuta la acción si se mantiene el tiempo necesario.
        """
        current_time = time.time()

        # Si está en tiempo de espera (cooldown), ignorar solicitudes
        if current_time - self.last_action_time < self.cooldown_time:
            return

        # Si se detecta una nueva inclinación
        if tilt != self.previous_tilt:
            self.tilt_timer = current_time
            self.previous_tilt = tilt

        # Si la inclinación se mantiene el tiempo suficiente
        elif self.tilt_timer and tilt and (current_time - self.tilt_timer >= self.hold_time):
            if tilt == "left":
                self.execute_action("task_browser")  # Abre el navegador
            elif tilt == "right":
                self.execute_action("task_alt_tab")  # Abre Alt+Tab

            # Registro del tiempo de la última acción y reset
            self.last_action_time = current_time
            self.tilt_timer = None
            self.previous_tilt = None

        # Reiniciar temporizador si no hay inclinación
        elif not tilt:
            self.tilt_timer = None
            self.previous_tilt = None
