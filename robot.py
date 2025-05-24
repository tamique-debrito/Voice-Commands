
from enum import Enum
from typing import Optional
from control.control import Control
from state_representation import BasketPosition, Location


from dataclasses import dataclass

from vision.vision import Vision


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

class Robot:
    """
    Contains logic for both percieving the state of the physical assembly and controlling the robot's actuators
    """
    def __init__(self) -> None:
        self.state = RobotState()
        self.vision = Vision()
        self.control = Control()
    
    def handle_command(self, action: RobotCommand):
        pass

    def update_items_in_basket(self, items: list[str]):
        self.state.items_in_basket = items

class MockRobot:
    """
    A mock simulator of the assembly that instantly completes every command successfully
    """
    def __init__(self) -> None:
        self.state = RobotState()

    def handle_command(self, command: RobotCommand):
        if command.action == BasketAction.LOWER_BASKET:
            self.state.basket_position = BasketPosition.LOWERED
        if command.action == BasketAction.RAISE_BASKET:
            self.state.basket_position = BasketPosition.RAISED
        if command.action == BasketAction.MOVE_BASKET_TO_LOCATION:
            assert self.state.basket_position == BasketPosition.RAISED, "Basket must be raised"
            assert command.location, "Need location specified"
            self.state.location = command.location
    
    def ask_update_item_list(self):
        new_list = input("Input new item list: ")
        if len(new_list) == 0:
            return
        elif new_list.lower() == "none":
            self.state.items_in_basket = None
        else:
            self.state.items_in_basket = new_list.split(",")


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
    state = RobotState()
    print(state)
    print(str(state))