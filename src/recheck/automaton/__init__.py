"""Automaton module for static analysis."""

from recheck.automaton.eps_nfa import EpsNFA, State, Transition
from recheck.automaton.eps_nfa_builder import build_eps_nfa
from recheck.automaton.ordered_nfa import OrderedNFA
from recheck.automaton.complexity_analyzer import ComplexityAnalyzer
from recheck.automaton.witness import WitnessGenerator
from recheck.automaton.checker import AutomatonChecker

__all__ = [
    "EpsNFA",
    "State",
    "Transition",
    "build_eps_nfa",
    "OrderedNFA",
    "ComplexityAnalyzer",
    "WitnessGenerator",
    "AutomatonChecker",
]
