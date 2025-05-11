from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        pass


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self):
        super().__init__()
    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return self.curr_sym == curr_char


class StarState(State):
    def __init__(self, checking_state: State) -> None:
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.regex_expr = regex_expr
        self.start = StartState()
        self.states: list[State] = [self.start]

        prev_state = self.start
        i = 0
        while i < len(regex_expr):
            char = regex_expr[i]

            if char == "*":
                checking_state = self.states[-1]
                star = StarState(checking_state)
                self.states[-2].next_states.remove(checking_state)
                self.states[-2].next_states.append(star)


                star.next_states.append(checking_state)
                checking_state.next_states.append(star)

                prev_state = star
                self.states.append(star)
                i += 1
                continue

            elif char == "+":
                checking_state = self.states[-1]
                plus = PlusState(checking_state)

                checking_state.next_states.append(plus)
                plus.next_states.append(plus)

                prev_state = plus
                self.states.append(plus)
                i += 1
                continue

            else:
                if char == ".":
                    state = DotState()
                else:
                    state = AsciiState(char)

                prev_state.next_states.append(state)
                prev_state = state
                self.states.append(state)
            i += 1

        self.termination = TerminationState()
        self.states[-1].next_states.append(self.termination)

        for idx, state in enumerate(self.states):
            if isinstance(state, StarState):
                for next_state in self.states[idx + 1:]:
                    state.next_states.append(next_state)
                    break

    def check_string(self, input_str: str) -> bool:
        queue = [(self.start, 0)]
        visited = set()

        while queue:
            state, idx = queue.pop()

            if (id(state), idx) in visited:
                continue
            visited.add((id(state), idx))

            if idx == len(input_str):
                if any(isinstance(s, TerminationState) for s in state.next_states):
                    return True
                for s in state.next_states:
                    queue.append((s, idx))
            else:
                for s in state.next_states:
                    if s.check_self(input_str[idx]):
                        queue.append((s, idx + 1))
                    elif isinstance(s, (StarState, PlusState)):
                        queue.append((s, idx))

        return False



if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
