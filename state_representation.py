from enum import Enum
from typing import Optional
from pydantic import BaseModel



class Events(Enum):
    ITEM_ADDED_TO_BASKET = "ITEM_ADDED_TO_BASKET"
    ITEM_REMOVED_FROM_BASKET = "ITEM_REMOVED_FROM_BASKET"

class Location(Enum):
    DESK = "DESK"
    BED = "BED"
    CLOSET = "CLOSET"

class BasketPosition(Enum):
    LOWERED = "LOWERED"
    RAISED = "RAISED"

