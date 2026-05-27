from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable


@dataclass
class ElementCandidate:
    selector: str
    text: str = ""
    role: str = ""
    test_id: str = ""


class HealingLocator:
    def __init__(self):
        self.heal_count = 0

    def find_best_match(self, expected_selector: str, candidates: Iterable[ElementCandidate]) -> ElementCandidate | None:
        best_candidate = None
        best_score = 0.0
        for candidate in candidates:
            values = [candidate.selector, candidate.text, candidate.role, candidate.test_id]
            score = max(SequenceMatcher(None, expected_selector, value).ratio() for value in values if value)
            if score > best_score:
                best_score = score
                best_candidate = candidate

        if best_candidate and best_candidate.selector != expected_selector:
            self.heal_count += 1
        return best_candidate
