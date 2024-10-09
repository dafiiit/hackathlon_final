#importieren der Klassen
from detection import ObjectDetector
from robotarm import Robotarm
from conveyorbelt import ConveyorBeltControl
from schranke import Schranke

#erstellen der Objekte
robotarm = Robotarm()
object_detector = ObjectDetector()
conveyor_control = ConveyorBeltControl()
schranke = Schranke()

state = 1
blockcounter = 1 #gibt an wie viele Blöcke schon aufgehoben wurden
while True:
    if state == 1:
        print("Roboter hebt nten Block auf")
        if robotarm.pick_up_block_n(blockcounter) == 42:
            print("picked up all blocks")
            break
        time.sleep(1000)
        blockcounter = blockcounter+1
        state = 2 
    elif state == 2:
        print("Fließbänder befödern den Block zur Kamera ")
        conveyor_control.control_belt(6, "vor")
        conveyor_control.control_stopper(6, "runter")
        conveyor_control.control_belt(5, "vor")
        conveyor_control.control_stopper(5, "runter")
        conveyor_control.control_belt(4, "vor")
        conveyor_control.control_stopper(4, "hoch")
        detection = conveyor_control.get_conveyor_detection(4)
        if detection: 
            state = 3
    elif state == 3:
        print("erkenne refrigerator/oven")
        refrigerator_detected, oven_detected = object_detector.detect_oven_refrigerator()
        print("lade die erkannten daten per API hoch")
        if oven_detected: 
            state = 4
        elif refrigerator_detected:
            state = 5
        else: 
            print("detected nothing, trying again")
            state = 3
    elif state == 4:
        print("schließe die Schranke")
        if schranke.schließe_schranke():
            state = 5
    elif state == 5:
        print("betreibe die Fließbänder nach der Kamera")
        conveyor_control.control_stopper(4, "runter")
        conveyor_control.control_belt(4, "vor")
        conveyor_control.control_stopper(3, "runter")
        conveyor_control.control_belt(3, "vor")
        conveyor_control.control_stopper(2, "runter")
        conveyor_control.control_belt(2, "vor")
        time.sleep(10000)
        state = 6
    elif state == 6:
        print("öffne die Schranke")
        if schranke.öffne_schranke():
            state = 1
    else:
        return "Ungültiger Wert"

