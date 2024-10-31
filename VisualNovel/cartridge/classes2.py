import re


class Transition:
    def __init__(self, trigger, next_state_label):
        self.trigger = trigger
        self.next_state_label = next_state_label

    def is_triggered(self, info):
        return self.trigger == info

    def apply_to_menu(self, mymenu):
        mymenu.add_item(self.trigger, self.next_state_label)


class State:
    def __init__(self, label, message, transitions, image=None, is_initial=False, is_terminal=False):
        self.label = label
        self.message = message
        self.transitions = transitions
        self.image = image
        self._initial = is_initial
        self._terminal = is_terminal

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
    def __init__(self, automata_storage):
        self.states = {}
        self.current_state_label = None
        self.automata_storage = automata_storage  # dep injection
        self.inner_data = None

    def load_from_json(self, data):
        self.inner_data = data
        #with open(file_path, 'r') as f:
        #    data = json.load(f)
        for state_data in data['states']:
            transitions = [Transition(t['trigger'], t['next_state']) for t in state_data.get('transitions', [])]
            state = State(
                state_data['label'],
                state_data['msg'],
                transitions,
                image=state_data.get('image', None),
                is_initial=state_data.get('initial', False),
                is_terminal=state_data.get('terminal', False)
            )
            self.states[state.label] = state
        self.reset()

    def handle_input(self, info) -> int:
        """
        Advances to the next state based on input

        :param info: text
        :return: 0 (no transition), 1 (simple transition), 2 (transition to another automaton)
        """
        next_state_label = self.get_current_state().process_input(info)
        if next_state_label is None:
            return 0

        if re.match(r'encounter_\w+', next_state_label):
            self.load_from_json(self.automata_storage[next_state_label])
            return 2

        self.current_state_label = next_state_label
        return 1

    def get_current_state(self):
        return self.states[self.current_state_label]

    def reset(self):
        for state in self.states.values():
            if state.is_initial():
                self.current_state_label = state.label
                break
        else:
            raise ValueError("No initial state defined in the JSON file.")

    def display_image(self):
        current_state = self.get_current_state()
        if current_state.image:
            print(f"Image: {current_state.image}")
