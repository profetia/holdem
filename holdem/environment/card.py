from typing import Dict, List

valid_suit: List[str] = ["S", "H", "D", "C", "BJ", "RJ"]
valid_rank: List[str] = [
    "A",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "T",
    "J",
    "Q",
    "K",
]

rank_map: Dict[str, int] = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

rank_lookup: str = "23456789TJQKA"
suit_lookup: str = "SCDH"


class Card:
    def __init__(self, suit: str, rank: str) -> None:
        self.suit: str = suit
        self.rank: str = rank

    def __eq__(self, other: "Card") -> bool:
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        suit_index: int = valid_suit.index(self.suit)
        rank_index: int = valid_rank.index(self.rank)
        return 100 * suit_index + rank_index

    def __str__(self) -> str:
        return self.index()

    def index(self) -> str:
        return self.suit + self.rank
