from dataclasses import dataclass
from enum import Enum
from pyfirmata import Arduino, util

TRANSLATION_MOTOR_PIN_A = 7
TRANSLATION_MOTOR_PIN_B = 8

RAISE_LOWER_MOTOR_PIN_A = 12
RAISE_LOWER_MOTOR_PIN_B = 13

PORT = 'COM3'

class MotorDirection(Enum):
    LEFT = 1
    RIGHT = 2
    STILL = 3 # No movement

@dataclass
class Motor:
    # The pin numbers that control the motor
    pin_a: int
    pin_b: int

    def set_dir(self, board: Arduino, motor_direction: MotorDirection):
        set_a = 1 if motor_direction == MotorDirection.LEFT else 0
        set_b = 1 if motor_direction == MotorDirection.RIGHT else 0
        board.digital[self.pin_a].write(set_a)
        board.digital[self.pin_b].write(set_b)

class Control:
    def __init__(self):
        self.board = Arduino(PORT)
        self.iter = util.Iterator(self.board)
        self.iter.start()
        self.translation = Motor(pin_a=TRANSLATION_MOTOR_PIN_A, pin_b=TRANSLATION_MOTOR_PIN_B)
        self.raise_lower = Motor(pin_a=RAISE_LOWER_MOTOR_PIN_A, pin_b=RAISE_LOWER_MOTOR_PIN_B)

    def set_translation(self, motor_direction: MotorDirection):
        self.translation.set_dir(self.board, motor_direction)

    def set_raise_lower(self, motor_direction: MotorDirection):
        self.raise_lower.set_dir(self.board, motor_direction)