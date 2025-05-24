from enum import Enum

from agent import Agent, AgentAction, AgentCommand
from robot import BasketAction, MockRobot, Robot, RobotCommand
from voice import MockVoiceListener, VoiceListener


class CoordinatorState(Enum):
    """
    Class to coordinate and route the inputs and outputs components of the system (robot, LLM, user, voice recognition, computer vision, etc.)
    Control/state flow
        Always start waiting for user input (USER_INPUT state)
        
        When the user provides input, this is then routed to the LLM (LLM_PROCESSING state)
            The LLM will then return a command.
            This command may bring the state back to USER_INPUT
            Or it may stay in the LLM_PROCESSING state, with the result of the operation being passed back to the LLM
    """
    USER_INPUT = "USER_INPUT"
    LLM_PROCESSING = "LLM_PROCESSING"
    ROBOT_MOVING = "ROBOT_MOVING"
    DONE = "DONE"

def translate_agent_command_to_robot_command(agent_command: AgentCommand):
    assert agent_command.action.is_robot_action(), "Can only translate a robot action"
    if agent_command.action == AgentAction.MOVE_BASKET_TO_LOCATION:
        assert agent_command.location is not None, "Need a location if moving basket"
        basket_action = BasketAction.MOVE_BASKET_TO_LOCATION
    elif agent_command.action == AgentAction.RAISE_BASKET:
        basket_action = BasketAction.RAISE_BASKET
    elif agent_command.action == AgentAction.LOWER_BASKET:
        basket_action = BasketAction.LOWER_BASKET
    else:
        raise ValueError(f"Unrecognized action {agent_command.action}")
    return RobotCommand(action=basket_action, location=agent_command.location)

class Coordinator:
    def __init__(self) -> None:
        self.state = CoordinatorState.USER_INPUT
        self.robot = MockRobot()
        self.agent = Agent()
        self.voice_listener = MockVoiceListener()
    
    def run(self):
        while self.state != CoordinatorState.DONE:
            user_input = self.voice_listener.get_voice()
            self.robot.ask_update_item_list()
            self.handle_user_input(user_input)

    def user_communication(self, info):
        print(f"################ USER COMMUNICATION:\n{info}")
    
    def handle_user_input(self, user_input):
        self.state = CoordinatorState.LLM_PROCESSING
        self.agent.add_input(user_input=user_input, system_input=str(self.robot.state))
        done = False
        while not done: # Continue processing results until the LLM is either done or requires user input
            agent_command = self.agent.process_input()
            if agent_command.action.is_robot_action():
                robot_command = translate_agent_command_to_robot_command(agent_command)
                self.state = CoordinatorState.ROBOT_MOVING
                self.robot.handle_command(robot_command)
                self.agent.add_input(system_input=str(self.robot.state))
                self.state = CoordinatorState.LLM_PROCESSING
            elif agent_command.action == AgentAction.SPECIFY_PLAN:
                self.state = CoordinatorState.LLM_PROCESSING
            elif agent_command.action.is_wait_user_input_action():
                self.user_communication(agent_command.user_message)
                self.state = CoordinatorState.USER_INPUT
                done = True
            elif agent_command.action == AgentAction.GOAL_COMPLETED:
                self.user_communication("Agent considers goal completed")
                self.state = CoordinatorState.DONE
                done = True
        return
