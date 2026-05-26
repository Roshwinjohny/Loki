import sys
import os
import subprocess
import pyttsx3
import speech_recognition as sr
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ui",
            "main_window.ui"
        )
        uic.loadUi(ui_path, self)

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300

        self.is_listening = False
        self.wake_words = ["hey loki", "loki"]

        self.initialize_ui()
        self.start_wake_word_loop()

    def initialize_ui(self):
        self.set_status("Status: Loki is online")
        self.log_message("Loki initialized successfully.")
        self.log_message("Say 'Hey Loki' to wake me up.")

    def set_status(self, text):
        self.statusLabel.setText(text)

    def log_message(self, text):
        self.transcriptTextEdit.appendPlainText(text)

    def clear_transcript(self):
        self.transcriptTextEdit.clear()

    def speak(self, text):
        self.log_message(f"Loki: {text}")

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except RuntimeError as e:
            self.log_message(f"TTS error: {e}")
            self.set_status("Status: TTS error")

    def start_wake_word_loop(self):
        self.wake_timer = QTimer(self)
        self.wake_timer.timeout.connect(self.listen_for_wake_word)
        self.wake_timer.start(1000)

    def listen_for_wake_word(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.set_status("Status: Waiting for wake word...")

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)

            try:
                text = self.recognizer.recognize_google(audio, language="en-GB").lower().strip()
                self.log_message(f'Heard: "{text}"')

                if any(wake_word in text for wake_word in self.wake_words):
                    self.log_message("Wake word detected")
                    self.set_status("Status: Wake word detected")
                    self.listen_for_command()
                else:
                    self.set_status("Status: Waiting for wake word...")

            except sr.UnknownValueError:
                pass

            except sr.RequestError as e:
                self.log_message(f"Speech recognition service error: {e}")
                self.set_status("Status: Recognition service error")

        except Exception:
            pass

        self.is_listening = False

    def listen_for_command(self):
        self.set_status("Status: Listening for command...")
        self.log_message("Listening for command...")

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

            try:
                text = self.recognizer.recognize_google(audio, language="en-GB")
                self.log_message(f'You said: "{text}"')
                self.set_status("Status: Processing command...")
                self.process_command(text)

            except sr.UnknownValueError:
                self.log_message("Could not understand the command")
                self.set_status("Status: Command not understood")

            except sr.RequestError as e:
                self.log_message(f"Speech recognition service error: {e}")
                self.set_status("Status: Recognition service error")

        except Exception as e:
            self.log_message(f"Runtime error: {e}")
            self.set_status("Status: Runtime error")

    def open_chrome(self):
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                return True

        self.log_message("Chrome executable not found.")
        self.set_status("Status: Chrome not found")
        return False

    def process_command(self, text):
        command = text.lower().strip()

        if "open chrome" in command:
            opened = self.open_chrome()
            if opened:
                self.log_message("Loki: Opening Chrome")
                self.set_status("Status: Chrome opened")
            else:
                self.log_message("Loki: I could not find Chrome on this computer")
                self.set_status("Status: Chrome not found")

        else:
            self.log_message(f"Loki: I heard {command}")
            self.set_status("Status: Command processed")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())