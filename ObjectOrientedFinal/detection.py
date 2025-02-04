import cv2
import os
import random
import time
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self):
        # Lade das YOLO-Modell
        self.model = YOLO("yolo11n.pt")
        self.temp_image_path = "/tmp/captured_image.jpg"
        self.fridge_folder = "refrigerator_data"
        self.oven_folder = "oven_data"
        self.train_folder = "train_data"
        self.val_folder = "val_data"
        self.create_folders()

    def create_folders(self):
        # Erstelle Ordner für Trainings- und Validierungsdaten
        os.makedirs(self.fridge_folder, exist_ok=True)
        os.makedirs(self.oven_folder, exist_ok=True)
        os.makedirs(self.train_folder, exist_ok=True)
        os.makedirs(self.val_folder, exist_ok=True)

    def capture_image(self):
        # Nimm ein Foto mit rpicam-still auf
        os.system(f'rpicam-still -o {self.temp_image_path} -t 1')  # 1 Sekunde für die Kameraumstellung
        return self.temp_image_path

    def detect(self):
        try:
            self.capture_image()
            frame = cv2.imread(self.temp_image_path)
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            if frame is None:
                raise ValueError("Error reading the captured image.")
            results = self.model(frame)
            return results
        except Exception as e:
            print(f"Error during detection: {str(e)}")
            return None
    
    def detect_oven_refrigerator(self):
        results = self.detect()
        if results is None:
            return False, False
        # Überprüfen, ob Kühlschrank oder Ofen erkannt wurde
        detected_classes = [result.cls for result in results[0].boxes]
        refrigerator_detected = 'refrigerator' in detected_classes
        oven_detected = 'oven' in detected_classes 
         
        # Rückgabe der Erkennungswerte
        return refrigerator_detected, oven_detected

    def split_data(self, train_ratio=0.8):
        # Aufteilung der Daten in Trainings- und Validierungssets
        def move_files(data_folder, target_train_folder, target_val_folder):
            files = os.listdir(data_folder)
            random.shuffle(files)
            split_point = int(len(files) * train_ratio)
            train_files = files[:split_point]
            val_files = files[split_point:]

            for file in train_files:
                os.rename(os.path.join(data_folder, file), os.path.join(target_train_folder, file))
            for file in val_files:
                os.rename(os.path.join(data_folder, file), os.path.join(target_val_folder, file))

        # Kühlschrank- und Ofenbilder aufteilen
        move_files(self.fridge_folder, os.path.join(self.train_folder, "fridge"), os.path.join(self.val_folder, "fridge"))
        move_files(self.oven_folder, os.path.join(self.train_folder, "oven"), os.path.join(self.val_folder, "oven"))
        print("Daten aufgeteilt in Trainings- und Validierungssets.")

    def retrain(self):
        results = self.model.train(data="custom_coco.yaml", epochs=100, imgsz=640)

    def preview(self):
        results = self.detect()
        # Ergebnisse rendern
        annotated_frame = results[0].plot()

        # Zeige die Ergebnisse an
        cv2.imshow('YOLOv11', annotated_frame)
        if cv2.waitKey(1) == ord('q'):
            print("Cant stop yet :(")
        time.sleep(10000)
        # Schließe das Fenster
        cv2.destroyAllWindows()
        
# Wird ausgeführt wenn dieses Programm direkt ausgeführt wird
if __name__ == "__main__":
    # Objekt der Klasse erstellen und die detect Methode ausführen
    detector = ObjectDetector()
    oven, refrigerator = detector.detect_oven_refrigerator()
    print("Oven: ")
    print(oven)
    detector.preview()

    #refrigerator, oven = detector.detect_oven_refrigerator()
    #print(f"Kühlschrank erkannt: {refrigerator}, Ofen erkannt: {oven}")
