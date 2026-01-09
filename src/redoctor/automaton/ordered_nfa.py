"""Ordered NFA with priority-aware transitions."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple

from redoctor.automaton.eps_nfa import EpsNFA, State, Transition, TransitionType
from redoctor.unicode.ichar import IChar


@dataclass
class OrderedNFA:
    """NFA with ordered (prioritized) transitions.

    This is used for analyzing backtracking behavior where
    transition order matters.

    Attributes:
        states: Set of all states.
        initial: Initial state.
        accepting: Set of accepting states.
        transitions: Transitions grouped by source state and ordered by priority.
        multi_transitions: Maps (state, char_key) to count of paths reaching that transition.
                          A count > 1 indicates EDA (multiple epsilon paths to same char transition).
    """

    states: Set[State] = field(default_factory=set)
    initial: Optional[State] = None
    accepting: Set[State] = field(default_factory=set)
    transitions: Dict[State, List[Transition]] = field(default_factory=dict)
    multi_transitions: Dict[Tuple[State, State], int] = field(default_factory=dict)

    @classmethod
    def from_eps_nfa(cls, eps_nfa: EpsNFA) -> "OrderedNFA":
        """Convert an epsilon-NFA to an ordered NFA by eliminating epsilon transitions.

        For ambiguity detection, we count the number of epsilon PATHS that lead
        to each character transition, not just whether the transition is reachable.

        For patterns like (a+)+:
        - From state S, we might reach the 'a' transition via multiple epsilon paths
        - Path 1: S -> inner_loop_entry -> char_trans
        - Path 2: S -> outer_loop -> inner_loop_entry -> char_trans
        - These multiple paths = EDA (exponential degree of ambiguity)

        This is the key insight from recheck's AutomatonChecker.
        """
        ordered = cls()
        ordered.states = set(eps_nfa.states)
        ordered.initial = eps_nfa.initial
        ordered.accepting = set(eps_nfa.accepting)

        # Track multi-transitions: how many epsilon paths lead to each char transition
        multi_trans_count: Dict[Tuple[State, State], int] = {}

        # For each state, collect character transitions reachable through epsilon
        for state in eps_nfa.states:
            ordered.transitions[state] = []

            # Count the number of EPSILON PATHS to each intermediate state
            # that has a character transition. This is different from just
            # counting which states are in the closure - we need to count paths.
            path_counts_to_intermediate = cls._count_epsilon_paths(eps_nfa, state)

            # Now for each intermediate state with character transitions,
            # check if there are multiple epsilon paths to it
            trans_by_priority: Dict[int, List[Transition]] = {}
            seen_trans: Set[Tuple[State, Optional[IChar]]] = set()

            for interm_state, num_paths in path_counts_to_intermediate.items():
                for trans in eps_nfa.transitions_from(interm_state):
                    if trans.type == TransitionType.CHAR and trans.char:
                        # Deduplicate transitions with same target
                        trans_key = (trans.target, trans.char)
                        if trans_key in seen_trans:
                            continue
                        seen_trans.add(trans_key)

                        new_trans = Transition(
                            source=state,
                            target=trans.target,
                            type=TransitionType.CHAR,
                            char=trans.char,
                            priority=trans.priority,
                        )
                        prio = trans.priority
                        if prio not in trans_by_priority:
                            trans_by_priority[prio] = []
                        trans_by_priority[prio].append(new_trans)

                        # Track if there are multiple paths to this transition
                        if num_paths > 1:
                            existing = multi_trans_count.get((state, trans.target), 0)
                            multi_trans_count[(state, trans.target)] = max(
                                existing, num_paths
                            )

            # Sort by priority and add
            for prio in sorted(trans_by_priority.keys()):
                ordered.transitions[state].extend(trans_by_priority[prio])

            # Check if any state in epsilon closure is accepting
            closure = eps_nfa.epsilon_closure({state})
            if closure & eps_nfa.accepting:
                ordered.accepting.add(state)

        ordered.multi_transitions = multi_trans_count
        return ordered

    @classmethod
    def _count_epsilon_paths(cls, eps_nfa: EpsNFA, start: State) -> Dict[State, int]:
        """Count the number of epsilon paths from start to each reachable state.

        This uses dynamic programming to count paths, not just reachability.
        For a state that can be reached via multiple epsilon paths, this will
        return a count > 1.

        For example, in (a+)+, from the state after reading 'a':
        - The inner loop entry state can be reached directly (1 path)
        - It can also be reached via the outer loop re-entry (1 more path)
        - Total: 2 paths, indicating EDA
        """
        # path_count[state] = number of distinct epsilon paths from start to state
        path_count: Dict[State, int] = {start: 1}
        visited_order: List[State] = []

        # BFS to find topological order (though cycles are possible in epsilon graphs)
        # For cycles, we need to detect them and mark as having infinite paths
        from collections import deque

        queue = deque([start])
        in_queue: Set[State] = {start}

        while queue:
            current = queue.popleft()
            visited_order.append(current)

            for trans in eps_nfa.transitions_from(current):
                if trans.is_epsilon():
                    target = trans.target
                    if target not in path_count:
                        path_count[target] = 0

                    # Add paths from current to target
                    path_count[target] += path_count[current]

                    # If target already processed but we found more paths, that's a cycle
                    # In that case, mark as having "many" paths (2+ is enough for EDA)
                    if target in in_queue:
                        # Cycle detected - this state has multiple paths
                        path_count[target] = max(path_count[target], 2)
                    elif target not in in_queue:
                        queue.append(target)
                        in_queue.add(target)

        return path_count

    def has_multi_transitions(self) -> bool:
        """Check if there are multi-transitions (EDA indicator)."""
        return len(self.multi_transitions) > 0

    def get_transitions(self, state: State) -> List[Transition]:
        """Get transitions from a state in priority order."""
        return self.transitions.get(state, [])

    def get_char_transitions(self, state: State, c: int) -> List[Transition]:
        """Get transitions matching a character."""
        result = []
        for trans in self.get_transitions(state):
            if trans.matches(c):
                result.append(trans)
        return result

    def size(self) -> int:
        """Return number of states."""
        return len(self.states)

    def transition_count(self) -> int:
        """Return total number of transitions."""
        return sum(len(t) for t in self.transitions.values())


@dataclass(frozen=True)
class NFAStatePair:
    """A pair of NFA states for product automaton construction."""

    state1: State
    state2: State

    def __repr__(self) -> str:
        return f"({self.state1.id}, {self.state2.id})"


def build_product_nfa(
    nfa: OrderedNFA,
) -> Tuple[Dict[NFAStatePair, List[Tuple[IChar, NFAStatePair]]], Set[NFAStatePair]]:
    """Build a product automaton for ambiguity detection.

    The product automaton has states (q1, q2) where q1 and q2 are states
    from the original NFA. An accepting state in the product means
    there are two different paths to reach the same state.

    Returns:
        Tuple of (transitions dict, set of reachable pairs).
    """
    if nfa.initial is None:
        return {}, set()

    transitions: Dict[NFAStatePair, List[Tuple[IChar, NFAStatePair]]] = {}
    visited: Set[NFAStatePair] = set()
    stack: List[NFAStatePair] = []

    initial_pair = NFAStatePair(nfa.initial, nfa.initial)
    stack.append(initial_pair)

    while stack:
        pair = stack.pop()
        if pair in visited:
            continue
        visited.add(pair)

        trans1 = nfa.get_transitions(pair.state1)
        trans2 = nfa.get_transitions(pair.state2)

        pair_transitions: List[Tuple[IChar, NFAStatePair]] = []

        for t1 in trans1:
            for t2 in trans2:
                if t1.char and t2.char:
                    # Check if characters overlap
                    overlap = t1.char.intersect(t2.char)
                    if overlap:
                        next_pair = NFAStatePair(t1.target, t2.target)
                        pair_transitions.append((overlap, next_pair))
                        if next_pair not in visited:
                            stack.append(next_pair)

        if pair_transitions:
            transitions[pair] = pair_transitions

    return transitions, visited
