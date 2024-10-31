import json


class Transition:
    def __init__(self, trigger, next_state_label):
        self.trigger = trigger
        self.next_state_label = next_state_label

    def is_triggered(self, info):
        return self.trigger == info

    def apply_to_menu(self, mymenu):
        mymenu.add_item(self.trigger, self.next_state_label)


class State:
    # Represents a state within the finite-state automaton, managing transitions
    def __init__(self, label, message, transitions, is_initial=False, is_terminal=False):
        self.label = label
        self.message = message
        self.transitions = transitions
        self._initial = is_initial
        self._terminal = is_terminal  # Renamed to avoid method conflict

    def process_input(self, info):
        # Processes input to determine the next state
        if self.is_terminal():
            return None
            # raise RuntimeError('Attempting to act while in a terminal state')
        for transition in self.transitions:
            if transition.is_triggered(info):
                return transition.next_state_label
        
    def is_terminal(self):
        return self._terminal

    def is_initial(self):
        return self._initial


class Automaton:
    # Manages the overall finite-state machine, loading states and handling transitions
    def __init__(self):
        self.states = {}
        self.current_state_label = ''

    def load_from_json(self, data):
        # Loads states and transitions from a JSON file
        #with open(file_path, 'r') as f:
        #    data = json.load(f)
        for state_data in data['states']:
            transitions = [Transition(t['trigger'], t['next_state']) for t in state_data.get('transitions', [])]
            state = State(
                state_data['label'],
                state_data['msg'],
                transitions,
                is_initial=state_data.get('initial', False),
                is_terminal=state_data.get('terminal', False)
            )
            self.states[state.label] = state
        self.reset()

    def handle_input(self, info):
        # Advances to the next state based on input
        next_state_label = self.get_current_state().process_input(info)
        if next_state_label:
            self.current_state_label = next_state_label
            return True
        return False

    def get_current_state(self):
        return self.states[self.current_state_label]

    def reset(self):
        # Resets to the initial state
        for state in self.states.values():
            if state.is_initial():
                self.current_state_label = state.label
                break
        else:
            raise ValueError("No initial state defined in the JSON file.")
