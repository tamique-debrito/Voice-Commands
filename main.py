from coordinator import Coordinator
import coordinator
from state_representation import BasketPosition, Location

if __name__ == "__main__":
    coordinator = Coordinator()
    try:
        coordinator.run()
    except Exception as e:
        print(e)

    print(coordinator.agent.state.history)