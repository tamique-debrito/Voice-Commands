from enum import Enum
from typing import Optional
from control.control import Control, MotorDirection
from state_representation import BasketPosition, Location


from dataclasses import dataclass

from vision.vision import Vision
import time

TRANSLATION_CALIBRATION_RATIO = 1.0 # The amount of time the translation motor needs to be run relative to the raise/lower motor while translating

CONTROL_PERIOD = 0.2 # The number of seconds in between reprocessing inputs and updating control signal

@dataclass
class RobotState:
    location: Location = Location.DESK
    basket_position: BasketPosition = BasketPosition.LOWERED
    items_in_basket: Optional[list[str]] = None

    def __str__(self) -> str:
        if self.items_in_basket is None:
            items_list = "None"
        else:
            items_list = "".join([f"\n - {item}" for item in self.items_in_basket])
        return \
f"""
The current location of the basket is: {self.location.value}
The basket is currently {self.basket_position.value}
The items currently in the basket are: {items_list}
"""

class BasketAction(Enum):
    MOVE_BASKET_TO_LOCATION = "MOVE_BASKET_TO_LOCATION"
    RAISE_BASKET = "RAISE_BASKET"
    LOWER_BASKET = "LOWER_BASKET"

    @staticmethod
    def get_descriptions():
        return \
f"""
- {BasketAction.MOVE_BASKET_TO_LOCATION.value}: Moves the basket to the specified location
- {BasketAction.RAISE_BASKET.value}: Raises the basket up out of the user's reach so that it can be moved
- {BasketAction.LOWER_BASKET.value}: Lowers the basket down within the user's reach so that they can add or retrieve items
"""

@dataclass
class RobotCommand:
    action: BasketAction
    location: Optional[Location] = None


class RobotBase:
    state: RobotState    
    def ask_update_item_list(self):
        new_list = input("Input new item list: ")
        if len(new_list) == 0:
            return
        elif new_list.lower() == "none":
            self.state.items_in_basket = None
        else:
            self.state.items_in_basket = new_list.split(",")


class MockRobot(RobotBase):
    """
    A mock simulator of the assembly that instantly completes every command successfully
    """
    def __init__(self) -> None:
        self.state = RobotState()

    def start(self):
        pass

    def handle_command(self, command: RobotCommand):
        if command.action == BasketAction.LOWER_BASKET:
            self.state.basket_position = BasketPosition.LOWERED
        if command.action == BasketAction.RAISE_BASKET:
            self.state.basket_position = BasketPosition.RAISED
        if command.action == BasketAction.MOVE_BASKET_TO_LOCATION:
            assert self.state.basket_position == BasketPosition.RAISED, "Basket must be raised"
            assert command.location, "Need location specified"
            self.state.location = command.location

class Robot(RobotBase):
    """
    Contains logic for both percieving the state of the physical assembly and controlling the robot's actuators
    """
    def __init__(self) -> None:
        self.state = RobotState()
        self.vision = Vision()
        self.vision.start()
        time.sleep(3)
        self.control = Control()
        self.stop_first_fn = self.control.set_raise_lower if TRANSLATION_CALIBRATION_RATIO >= 1.0 else self.control.set_translation # The function that will be called to reduce the speed of the motor that should be slower during translation
        self.stop_first_frac = min(TRANSLATION_CALIBRATION_RATIO, 1 / TRANSLATION_CALIBRATION_RATIO) # The fraction of the control interval after which to stop the motor that should be slower

    def start(self):
        pass

    def map_location_to_checkpoint(self, location: Location) -> int:
        return {
            Location.DESK: 0,
            Location.BED: 1,
            Location.CLOSET: 2
        }[location]
    
    def handle_command(self, command: RobotCommand):
        # Start vision system if not already running
        if not self.vision._process_started:
            self.vision.start()
            time.sleep(2)  # Give vision system time to initialize
        
        print(f"Robot command: {str(command)}")

        if command.action == BasketAction.LOWER_BASKET:
            # Keep lowering until vision system detects basket is lowered
            while True:
                info = self.vision.get_info(0)  # Use checkpoint 0 as reference
                if info is None:
                    continue
                _, raise_lower_state = info
                if raise_lower_state == -1: # Basket is lowered
                    self.state.basket_position = BasketPosition.LOWERED
                    break
                self.control.set_raise_lower(MotorDirection.COUNTERCLOCKWISE)
                time.sleep(CONTROL_PERIOD)
            self.control.set_raise_lower(MotorDirection.STILL)

        elif command.action == BasketAction.RAISE_BASKET:
            # Keep raising until vision system detects basket is raised
            while True:
                info = self.vision.get_info(self.map_location_to_checkpoint(self.state.location))
                if info is None:
                    continue
                _, raise_lower_state = info
                if raise_lower_state == +1: # Basket is raised
                    self.state.basket_position = BasketPosition.RAISED
                    break
                self.control.set_raise_lower(MotorDirection.CLOCKWISE)
                time.sleep(CONTROL_PERIOD)
            self.control.set_raise_lower(MotorDirection.STILL)

        elif command.action == BasketAction.MOVE_BASKET_TO_LOCATION:
            if not command.location:
                raise ValueError("Location must be specified for MOVE_BASKET_TO_LOCATION")
            
            # First ensure basket is raised
            if self.state.basket_position != BasketPosition.RAISED:
                self.handle_command(RobotCommand(BasketAction.RAISE_BASKET))

            target_checkpoint = self.map_location_to_checkpoint(command.location)

            # Move until we reach the target checkpoint
            while True:
                info = self.vision.get_info(target_checkpoint)
                if info is None:
                    continue
                print(f"Info: {info}")
                checkpoint_rel, _ = info
                
                if checkpoint_rel == 0:  # At target
                    self.state.location = command.location
                    break
                elif checkpoint_rel == 1:  # Need to move right
                    self.control.set_translation(MotorDirection.CLOCKWISE)
                    self.control.set_raise_lower(MotorDirection.CLOCKWISE)  # Keep basket raised
                else:  # Need to move left
                    self.control.set_translation(MotorDirection.COUNTERCLOCKWISE)
                    self.control.set_raise_lower(MotorDirection.COUNTERCLOCKWISE)  # Keep basket raised
                
                time.sleep(CONTROL_PERIOD * self.stop_first_frac) # account for the calibration ratio
                self.stop_first_fn(MotorDirection.STILL)
                time.sleep(CONTROL_PERIOD * (1 - self.stop_first_frac))

            # Stop motors
            self.control.set_translation(MotorDirection.STILL)
            self.control.set_raise_lower(MotorDirection.STILL)

    def update_items_in_basket(self, items: list[str]):
        self.state.items_in_basket = items

def get_system_description():
    return f"""
The basket is suspended on a wire and can be moved along the wire between locations.
At any given location, the basket can be lowered or raised.
Items can be added to or removed from the basket by the user. 

The system is subject to the following constraints:
- In order to move the basket, it must be in the raised position
- In order for the user to be able to add or remove items from the basket, it must be in the lowered position
These are the commands available for controlling the basket: {BasketAction.get_descriptions()}
"""

if __name__ == "__main__":
    print(RobotCommand(BasketAction.MOVE_BASKET_TO_LOCATION, location=Location.CLOSET))
    robot = Robot()
    print(robot.state)
    robot.start()
    robot.control.set_translation(MotorDirection.COUNTERCLOCKWISE)
    time.sleep(15)
    robot.control.set_translation(MotorDirection.STILL)
    
    robot.handle_command(RobotCommand(BasketAction.MOVE_BASKET_TO_LOCATION, location=Location.CLOSET))
    robot.handle_command(RobotCommand(BasketAction.MOVE_BASKET_TO_LOCATION, location=Location.DESK))
    robot.handle_command(RobotCommand(BasketAction.LOWER_BASKET))
    