from classes2 import *


if __name__ == '__main__':
    # Main loop for handling interaction across multiple NPCs
    current_file = 'encounter_1.json'
    automaton = Automaton()
    automaton.load_from_json(current_file)
    print('Automaton is ready for testing.')

    while True:
        curr_state = automaton.get_current_state()
        curr_message = curr_state.message
        formatted_text = "\n".join(textwrap.wrap(curr_message, width=56))
        print(tabulate([[formatted_text]], tablefmt="grid"))

        automaton.display_image()

        if curr_state.is_terminal():
            break

        transitions = curr_state.transitions
        for i, transition in enumerate(transitions):
            print(f'{i+1}/', '\n'.join(textwrap.wrap(transition.trigger, width=60)))
            print()
        choice = input('>>')
        
        selected_text = transitions[int(choice)-1].trigger
        next_state_label = automaton.handle_input(selected_text)
        
        # Check if next state indicates a new encounter
        if re.match(r'encounter_\w+', next_state_label):
            # Load new encounter
            current_file = f"{next_state_label}.json"
            automaton = Automaton()
            automaton.load_from_json(current_file)
            print(f"Switched to new encounter: {current_file}")
