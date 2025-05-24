from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from openai import OpenAI
from openai.types import responses
client = OpenAI()

from robot import get_system_description
from state_representation import Location

class AgentAction(Enum):
    REQUEST_ADDITIONAL_INFO = "REQUEST_ADDITIONAL_INFO"
    REQUEST_USER_ACTION = "REQUEST_USER_ACTION"
    SPECIFY_PLAN = "SPECIFY_PLAN"
    MOVE_BASKET_TO_LOCATION = "MOVE_BASKET_TO_LOCATION"
    RAISE_BASKET = "RAISE_BASKET"
    LOWER_BASKET = "LOWER_BASKET"
    GOAL_COMPLETED = "GOAL_COMPLETED"

    def is_robot_action(self):
        return self in [AgentAction.MOVE_BASKET_TO_LOCATION, AgentAction.RAISE_BASKET, AgentAction.LOWER_BASKET]

    def is_wait_user_input_action(self):
        return self in [AgentAction.REQUEST_ADDITIONAL_INFO, AgentAction.REQUEST_USER_ACTION]

    @staticmethod
    def get_descriptions():
        return \
f"""
- {AgentAction.REQUEST_ADDITIONAL_INFO.value}: Request the user to provide additional information about the situation.
- {AgentAction.REQUEST_USER_ACTION.value}: Request the user to perform an action as part of accomplishing the goal. If user action is required, this action MUST be used.
- {AgentAction.SPECIFY_PLAN.value}: Specify the plan that you will follow to accomplish the task.
- {AgentAction.MOVE_BASKET_TO_LOCATION.value}: Move basket to specified location.
- {AgentAction.RAISE_BASKET.value}: Raise the basket.
- {AgentAction.LOWER_BASKET.value}: Lower the basket.
- {AgentAction.GOAL_COMPLETED.value}: Signal that the goal has been accomplished.
"""

@dataclass
class AgentCommand(BaseModel):
    action: AgentAction
    location: Optional[Location]
    user_message: Optional[str]
    plan: Optional[str]

class InteractionState(Enum):
    AWAITING_REQUEST = 1
    AWAITING_ADDITIONAL_INFO = 2
    AWAITING_COMMAND_COMPLETION = 3
    REQUEST_RESOLVED = 4

@dataclass
class HistoryElement:
    user_input: Optional[str] = None
    agent_response: Optional[str] = None
    system_input: Optional[str] = None

    def to_llm_input(self) -> responses.response_input_param.ResponseInputItemParam:
        if self.user_input is not None:
            return {"role": "user", "content": self.user_input}
        elif self.system_input is not None:
            return {"role": "system", "content": self.system_input}
        elif self.agent_response is not None:
            return {"role": "assistant", "content": self.agent_response}
        else:
            raise ValueError("Invalid history item")
@dataclass
class AgentState:
    current_user_request: str = ""
    interaction_state: InteractionState = InteractionState.AWAITING_REQUEST
    history: list[HistoryElement] = field(default_factory=list)
    
    def record_user_input(self, user_input):
        print(f"#### user_input: {user_input}")
        self.history.append(HistoryElement(user_input=user_input))

    def record_system_input(self, system_input):
        print(f"#### system_input: {system_input}")
        self.history.append(HistoryElement(system_input=system_input))

    def record_agent_response(self, agent_response):
        print(f"#### agent_response: {agent_response}")
        self.history.append(HistoryElement(agent_response=agent_response))


class Agent:
    def __init__(self) -> None:
        self.state = AgentState()
        self.state.record_system_input(get_scenario_prompt())
    
    def add_input(self, user_input: Optional[str] = None, system_input: Optional[str] = None):
        if user_input is not None:
            self.state.record_user_input(user_input)
        if system_input is not None:
            self.state.record_system_input(system_input)

    def process_input(self) -> AgentCommand:
        print("Processing input")
        response = client.responses.parse(
            model="gpt-4o-mini",
            temperature=0.0,
            input=[
                history_item.to_llm_input() for history_item in self.state.history
            ],
            text_format=AgentCommand,
        )

        command = response.output_parsed
        if command is None:
            raise ValueError("Didn't get a command")
        self.state.record_agent_response(str(command))
        return command
                

def get_scenario_prompt():
    return \
f"""You are a helpful agent responsible for moving around a robotic basket to assist the user in their activities.
You must listen to and understand stated commands and goals and then devise a plan to meet acheive the user's desired state via controlling the robot basket.
If there is additional information needed to plan for the task, you should respond by asking for this information, then proceed with planning and executing the task.
Once you have determined the goal is met based on updates from the user and the robot's state, you should signal that the goal has been accomplished.

Here is a detailed description of the system:
{get_system_description()}

In assisting the user in their goal, you have the ability to control the robot basket, request more information about the situation, or request the user perform a particular action.
Here is a specific list of the actions available to you:
{AgentAction.get_descriptions()}
You may only take one action at a time.

The user will make an initial request and information about the current state of the robot will be provided.
At that point you should either provide your plan or if more information is needed to devise a plan, ask for it.
"""