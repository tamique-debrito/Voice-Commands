from dataclasses import dataclass
from enum import Enum
from time import sleep
from pyfirmata import Arduino, util

import control

TRANSLATION_MOTOR_PIN_A = 12
TRANSLATION_MOTOR_PIN_B = 13

RAISE_LOWER_MOTOR_PIN_A = 7
RAISE_LOWER_MOTOR_PIN_B = 8

PORT = 'COM3'

class MotorDirection(Enum):
    COUNTERCLOCKWISE = 1
    CLOCKWISE = 2
    STILL = 3 # No movement

@dataclass
class Motor:
    # The pin numbers that control the motor
    pin_a: int
    pin_b: int

    def set_dir(self, board: Arduino, motor_direction: MotorDirection):
        set_a = 1 if motor_direction == MotorDirection.COUNTERCLOCKWISE else 0
        set_b = 1 if motor_direction == MotorDirection.CLOCKWISE else 0
        board.digital[self.pin_a].write(set_a)
        board.digital[self.pin_b].write(set_b)

class Control:
    def __init__(self):
        self.board = Arduino(PORT)
        self.iter = util.Iterator(self.board)
        self.iter.start()
        self.translation = Motor(pin_a=TRANSLATION_MOTOR_PIN_A, pin_b=TRANSLATION_MOTOR_PIN_B)
        #self.raise_lower = Motor(pin_a=RAISE_LOWER_MOTOR_PIN_A, pin_b=RAISE_LOWER_MOTOR_PIN_B)

    def set_translation(self, motor_direction: MotorDirection):
        self.translation.set_dir(self.board, motor_direction)

    def set_raise_lower(self, motor_direction: MotorDirection):
        ...#self.raise_lower.set_dir(self.board, motor_direction)

def simple_test():
    control = Control()
    print("Testing translation motor")
    control.set_translation(MotorDirection.CLOCKWISE)
    sleep(0.1)
    control.set_translation(MotorDirection.STILL)
    sleep(2)
    control.set_translation(MotorDirection.COUNTERCLOCKWISE)
    sleep(0.1)
    control.set_translation(MotorDirection.STILL)
    sleep(2)


    print("Testing raise/lower motor")
    control.set_raise_lower(MotorDirection.CLOCKWISE)
    sleep(0.1)
    control.set_raise_lower(MotorDirection.STILL)
    sleep(2)
    control.set_raise_lower(MotorDirection.COUNTERCLOCKWISE)
    sleep(0.1)
    control.set_raise_lower(MotorDirection.STILL)
    sleep(2)

if __name__ == "__main__":
    #test motor
    # The motors are NOT consistent in terms of how connecting the red/black wires to the output pins corresponds to a clockwise/counterclockwise direction.
    # rotation direction is in reference to to the shaft on the opposite side of where the leads attach
    control = Control()
    
    control.set_translation(MotorDirection.CLOCKWISE)
    sleep(15)
    control.set_translation(MotorDirection.COUNTERCLOCKWISE)
    sleep(0)
    control.set_translation(MotorDirection.STILL)
    # print("Testing retracting from full extension")
    # for i in range(10):
    #     control.set_raise_lower(MotorDirection.COUNTERCLOCKWISE)
    #     control.set_translation(MotorDirection.COUNTERCLOCKWISE)
    #     sleep(0.5)
    #     control.set_raise_lower(MotorDirection.STILL)
    #     sleep(0.5)
    #     control.set_translation(MotorDirection.STILL)
    # control.set_translation(MotorDirection.STILL)
    # control.set_raise_lower(MotorDirection.STILL)