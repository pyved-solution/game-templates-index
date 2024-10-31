from classes1 import *


if __name__ == '__main__':
    # Entry point for running the automaton demo
    from tabulate import tabulate
    import textwrap

    automaton = Automaton()
    automaton.load_from_json('conv_simple.json')
    print('Automaton is ready for testing.')

    while True:
        # Interaction loop for navigating states
        curr_state = automaton.get_current_state()
        curr_message = curr_state.message
        formatted_text = "\n".join(textwrap.wrap(curr_message, width=56))
        print(tabulate([[formatted_text]], tablefmt="grid"))
        print()
        if curr_state.is_terminal():
            break

        # Display available transitions for the current state
        transitions = automaton.get_current_state().transitions
        for i, transition in enumerate(transitions):
            print(f'{i+1}/', '\n'.join(textwrap.wrap(transition.trigger, width=60)))
            print()
        choice = input('>>')
        selected_text = transitions[int(choice)-1].trigger
        automaton.handle_input(selected_text)
