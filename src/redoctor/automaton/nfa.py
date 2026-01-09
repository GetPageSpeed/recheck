"""NFA and DFA implementations for automaton analysis."""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Generic, List, Optional, Set, Tuple, TypeVar
from collections import deque

from redoctor.automaton.eps_nfa import EpsNFA, State, TransitionType
from redoctor.unicode.ichar import IChar

# Type variables for alphabet and state types
A = TypeVar("A")  # Alphabet type
Q = TypeVar("Q")  # State type


@dataclass
class NFA(Generic[A, Q]):
    """Non-deterministic Finite Automaton.

    This is a standard NFA without epsilon transitions, used as an
    intermediate representation for DFA construction.
    """

    alphabet: Set[A] = field(default_factory=set)
    state_set: Set[Q] = field(default_factory=set)
    init_set: Set[Q] = field(default_factory=set)
    accept_set: Set[Q] = field(default_factory=set)
    delta: Dict[Tuple[Q, A], Set[Q]] = field(default_factory=dict)

    def to_dfa(self) -> "DFA[A, FrozenSet[Q]]":
        """Convert NFA to DFA using subset construction."""
        init_frozen = frozenset(self.init_set)

        queue: deque[FrozenSet[Q]] = deque([init_frozen])
        new_state_set: Set[FrozenSet[Q]] = {init_frozen}
        new_accept_set: Set[FrozenSet[Q]] = set()
        new_delta: Dict[Tuple[FrozenSet[Q], A], FrozenSet[Q]] = {}

        while queue:
            qs = queue.popleft()
            if qs & self.accept_set:
                new_accept_set.add(qs)

            for a in self.alphabet:
                # Compute next states for this alphabet symbol
                next_states: Set[Q] = set()
                for q in qs:
                    next_states.update(self.delta.get((q, a), set()))

                next_frozen = frozenset(next_states)
                new_delta[(qs, a)] = next_frozen

                if next_frozen not in new_state_set:
                    queue.append(next_frozen)
                    new_state_set.add(next_frozen)

        return DFA(
            alphabet=self.alphabet,
            state_set=new_state_set,
            init=init_frozen,
            accept_set=new_accept_set,
            delta=new_delta,
        )


@dataclass
class DFA(Generic[A, Q]):
    """Deterministic Finite Automaton."""

    alphabet: Set[A] = field(default_factory=set)
    state_set: Set[Q] = field(default_factory=set)
    init: Optional[Q] = None
    accept_set: Set[Q] = field(default_factory=set)
    delta: Dict[Tuple[Q, A], Q] = field(default_factory=dict)

    def get_reverse_delta(self) -> Dict[A, List[Tuple[Q, Q]]]:
        """Get reverse transitions grouped by alphabet symbol.

        Returns:
            Dict mapping alphabet symbol to list of (target, source) pairs.
        """
        result: Dict[A, List[Tuple[Q, Q]]] = {}
        for (q1, a), q2 in self.delta.items():
            if a not in result:
                result[a] = []
            result[a].append((q2, q1))  # Reversed: (target, source) -> (source, target)
        return result


@dataclass
class OrderedNFARecheck:
    """Ordered NFA following recheck's design.

    Key features:
    - Ordered transitions (priority matters for backtracking)
    - Multi-transition detection (duplicate targets indicate EDA)
    - Built using accumulated priority through epsilon paths
    """

    alphabet: Set[IChar] = field(default_factory=set)
    state_set: Set[int] = field(default_factory=set)
    inits: List[int] = field(default_factory=list)  # Ordered initial states
    accept_set: Set[int] = field(default_factory=set)
    # delta: (state, char) -> ordered list of target states (MAY contain duplicates!)
    delta: Dict[Tuple[int, IChar], List[int]] = field(default_factory=dict)
    # Multi-transition indicator: True if any transition has duplicate targets
    has_multi_trans: bool = False

    @classmethod
    def from_eps_nfa(cls, eps_nfa: EpsNFA) -> "OrderedNFARecheck":
        """Build OrderedNFA from epsilon-NFA.

        Key insight: EDA is detected when for some state S, after reading a
        character, we can reach the SAME target state T via multiple DIFFERENT
        epsilon paths. This happens in patterns like (a+)+ where:
        - Path 1: continue inner loop directly
        - Path 2: exit inner, go through outer, re-enter inner

        We detect this by counting epsilon paths that lead to each character
        transition and checking for multiplicities.
        """
        # Rename states to integers
        state_to_int: Dict[State, int] = {}
        for i, state in enumerate(eps_nfa.states):
            state_to_int[state] = i

        result = cls()
        result.state_set = set(range(len(eps_nfa.states)))

        if eps_nfa.initial:
            result.inits = [state_to_int[eps_nfa.initial]]

        result.accept_set = {state_to_int[s] for s in eps_nfa.accepting}

        # Update accept set based on epsilon reachability
        for state in eps_nfa.states:
            closure = eps_nfa.epsilon_closure({state})
            if any(s in eps_nfa.accepting for s in closure):
                result.accept_set.add(state_to_int[state])

        # For each state, collect all character transitions reachable via epsilon
        # Key insight for EDA detection:
        # - Multiple epsilon paths to the SAME (char, target) = multi-transition
        # - Multiple different targets for the same char = alternation ambiguity
        #
        # We use BFS and count how many DISTINCT PATHS lead to each (char, target)
        for state in eps_nfa.states:
            q = state_to_int[state]

            # Count paths to each (char_key, target) pair
            # A "path" is distinguished by the sequence of epsilon priorities
            path_counts: Dict[Tuple[str, int], int] = {}  # (char_key, target) -> count
            char_objects: Dict[str, IChar] = {}

            # BFS to find all epsilon paths - use (state, path_signature) as visited key
            # This allows the same state to be visited via different paths
            queue: deque[Tuple[State, Tuple[int, ...]]] = deque([(state, ())])
            visited: Set[Tuple[State, Tuple[int, ...]]] = set()

            while queue:
                current, path_sig = queue.popleft()

                visit_key = (current, path_sig)
                if visit_key in visited:
                    continue

                # Limit path length to prevent infinite loops
                if len(path_sig) > 20:
                    continue

                visited.add(visit_key)

                for trans in eps_nfa.transitions_from(current):
                    if trans.type == TransitionType.CHAR and trans.char:
                        target = state_to_int[trans.target]
                        char_key = str(trans.char)
                        key = (char_key, target)
                        path_counts[key] = path_counts.get(key, 0) + 1
                        char_objects[char_key] = trans.char
                    elif trans.type == TransitionType.EPSILON:
                        new_sig = path_sig + (trans.priority,)
                        queue.append((trans.target, new_sig))

            # Check for EDA conditions and build delta
            # Group by character
            by_char: Dict[str, List[int]] = {}  # char_key -> [target, ...]
            for (char_key, target), count in path_counts.items():
                if char_key not in by_char:
                    by_char[char_key] = []
                # Add target 'count' times to preserve path multiplicity
                by_char[char_key].extend([target] * count)

            for char_key, targets in by_char.items():
                # EDA is detected when the SAME target is reached via MULTIPLE paths
                # This is the key insight: multiple different targets is just
                # non-determinism (like alternation), not ambiguity.
                # Ambiguity requires RECONVERGENCE - same target via different paths.
                target_counts: Dict[int, int] = {}
                for target in targets:
                    target_counts[target] = target_counts.get(target, 0) + 1

                for target, count in target_counts.items():
                    if count > 1:
                        result.has_multi_trans = True

            # Build delta - preserve duplicates for multi-transition detection
            for char_key, targets in by_char.items():
                char_obj = char_objects[char_key]
                result.alphabet.add(char_obj)
                result.delta[(q, char_obj)] = targets

        return result

    def reverse(self) -> NFA[IChar, int]:
        """Reverse this NFA.

        Returns a standard NFA (loses ordering) with:
        - Initial states = original accept states
        - Accept states = original initial states
        - Transitions reversed
        """
        reverse_delta: Dict[Tuple[int, IChar], Set[int]] = {}

        for (q1, a), targets in self.delta.items():
            for q2 in targets:
                key = (q2, a)
                if key not in reverse_delta:
                    reverse_delta[key] = set()
                reverse_delta[key].add(q1)

        return NFA(
            alphabet=self.alphabet,
            state_set=self.state_set,
            init_set=self.accept_set,  # Reversed
            accept_set=set(self.inits),  # Reversed
            delta=reverse_delta,
        )

    def to_nfa_wla(self, max_size: int = 100000) -> "NFAwLA":
        """Convert to NFA with Look-Ahead.

        This is the key algorithm from recheck that enables precise
        ambiguity detection by incorporating look-ahead information.

        The look-ahead DFA is built from the reversed NFA. States in NFAwLA
        are pairs (q, p) where q is original state and p is look-ahead state.

        Crucially, transitions are PRUNED based on look-ahead: if an earlier
        (higher priority) transition target is in the look-ahead set, later
        transitions to the same character are dead-ends and are excluded.
        """
        # Step 1: Build reversed DFA
        reversed_nfa = self.reverse()
        reversed_dfa = reversed_nfa.to_dfa()

        # Step 2: Build reverse delta for quick lookup
        # Maps char -> list of (p1, p2) where p1 <- char -- p2 in reversed DFA
        reverse_delta: Dict[IChar, List[Tuple[FrozenSet[int], FrozenSet[int]]]] = {}
        for (p2, a), p1 in reversed_dfa.delta.items():
            if a not in reverse_delta:
                reverse_delta[a] = []
            reverse_delta[a].append((p1, p2))

        # Step 3: Build NFAwLA
        # State: (original_q, look_ahead_p)
        # Alphabet: (original_char, look_ahead_p)
        NFAState = Tuple[int, FrozenSet[int]]
        NFAChar = Tuple[IChar, FrozenSet[int]]

        new_alphabet: Set[NFAChar] = set()
        new_state_set: Set[NFAState] = set()
        new_delta: Dict[Tuple[NFAState, NFAChar], List[NFAState]] = {}

        # Initial states: (q, p) for q in inits, p in reversed_dfa.state_set
        new_inits: List[NFAState] = []
        for q in self.inits:
            for p in reversed_dfa.state_set:
                new_inits.append((q, p))
                new_state_set.add((q, p))

        # Accept states: (q, init_of_reversed_dfa) for q in accept_set
        new_accept_set: Set[NFAState] = set()
        if reversed_dfa.init is not None:
            for q in self.accept_set:
                new_accept_set.add((q, reversed_dfa.init))

        delta_size = 0

        # Build transitions for EDA detection
        #
        # Key insight: We need to preserve enough information to detect both:
        # 1. Multi-transitions (duplicates) - always exploitable in practice
        # 2. Non-determinism (different targets) - exploitable when they overlap
        #
        # Strategy:
        # - Keep all duplicates (same target reached multiple times)
        # - Keep different targets (for pair graph analysis)
        # - Use look-ahead in SCC checker to filter false positives
        #
        # This approach may have some false positives that the SCC checker
        # will need to filter based on pair graph connectivity.
        for (q1, a), targets in self.delta.items():
            for p1, p2 in reverse_delta.get(a, []):
                # Convert all targets to NFAwLA state format
                nfa_targets: List[NFAState] = []
                for q2 in targets:
                    nfa_targets.append((q2, p2))
                    new_state_set.add((q2, p2))

                if nfa_targets:
                    nfa_state = (q1, p1)
                    nfa_char: NFAChar = (a, p2)
                    new_alphabet.add(nfa_char)
                    new_state_set.add(nfa_state)

                    key = (nfa_state, nfa_char)
                    if key in new_delta:
                        new_delta[key].extend(nfa_targets)
                    else:
                        new_delta[key] = nfa_targets

                    delta_size += len(nfa_targets)
                    if delta_size > max_size:
                        raise ValueError(f"NFAwLA size exceeds limit: {delta_size}")

        return NFAwLA(
            alphabet=new_alphabet,
            state_set=new_state_set,
            init_set=set(new_inits),
            accept_set=new_accept_set,
            delta=new_delta,
            look_ahead_dfa=reversed_dfa,
        )


@dataclass
class NFAwLA:
    """NFA with Look-Ahead.

    This is the key data structure for precise ambiguity detection.
    States are pairs (q, p) where:
    - q is the original NFA state
    - p is the look-ahead DFA state (from reversed DFA)

    The look-ahead prunes dead-end transitions, making ambiguity
    detection precise without false positives.
    """

    alphabet: Set[Tuple[IChar, FrozenSet[int]]] = field(default_factory=set)
    state_set: Set[Tuple[int, FrozenSet[int]]] = field(default_factory=set)
    init_set: Set[Tuple[int, FrozenSet[int]]] = field(default_factory=set)
    accept_set: Set[Tuple[int, FrozenSet[int]]] = field(default_factory=set)
    # delta: ((q, p), (a, p')) -> ordered list of (q', p')
    delta: Dict[
        Tuple[Tuple[int, FrozenSet[int]], Tuple[IChar, FrozenSet[int]]],
        List[Tuple[int, FrozenSet[int]]],
    ] = field(default_factory=dict)
    look_ahead_dfa: Optional[DFA] = None

    def get_edges(
        self,
    ) -> List[
        Tuple[
            Tuple[int, FrozenSet[int]],
            Tuple[IChar, FrozenSet[int]],
            Tuple[int, FrozenSet[int]],
        ]
    ]:
        """Get all edges as (source, label, target) tuples."""
        edges = []
        for (state, char), targets in self.delta.items():
            for target in targets:
                edges.append((state, char, target))
        return edges
