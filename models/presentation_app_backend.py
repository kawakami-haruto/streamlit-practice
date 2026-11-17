"""Backend logic for the simplified blackjack game."""

from dataclasses import dataclass, field
import random


Card = tuple[str, int]


@dataclass
class Round:
    """State for one blackjack round."""

    bet: int
    player_hand: list[Card] = field(default_factory=list)
    dealer_hand: list[Card] = field(default_factory=list)
    finished: bool = False
    result: str | None = None
    settled: bool = False


def create_deck() -> list[Card]:
    """Create and shuffle a standard 52-card deck."""
    suits = ("♠", "♥", "♦", "♣")
    return [(suit, rank) for suit in suits for rank in range(1, 14)]


def card_label(card: Card) -> str:
    """Return a display label for a card."""
    _, rank = card
    rank_labels = {1: "A", 11: "J", 12: "Q", 13: "K"}
    return f"{card[0]} {rank_labels.get(rank, str(rank))}"


def hand_value(hand: list[Card]) -> int:
    """Calculate the best blackjack value, treating aces as 1 or 11."""
    value = sum(11 if rank == 1 else min(rank, 10) for _, rank in hand)
    aces = sum(rank == 1 for _, rank in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def is_bust(hand: list[Card]) -> bool:
    return hand_value(hand) > 21


def start_round(bet: int, balance: int) -> Round:
    """Deal two cards to the player and dealer."""
    if balance < 1:
        raise ValueError("所持金がないため、ゲームを開始できません。")
    if not 1 <= bet <= balance:
        raise ValueError("掛け金は1円から所持金全額の範囲で指定してください。")

    deck = create_deck()
    random.shuffle(deck)
    return Round(
        bet=bet,
        player_hand=[deck.pop(), deck.pop()],
        dealer_hand=[deck.pop(), deck.pop()],
    )


def hit(round_state: Round) -> None:
    """Deal one card to the player."""
    if round_state.finished:
        raise ValueError("終了したラウンドにはヒットできません。")

    used = round_state.player_hand + round_state.dealer_hand
    available_cards = [card for card in create_deck() if card not in used]
    round_state.player_hand.append(random.choice(available_cards))
    if is_bust(round_state.player_hand):
        round_state.finished = True
        round_state.result = "bust"


def finish_round(round_state: Round) -> str:
    """Stand, play the dealer, and return the round result."""
    if round_state.finished:
        return round_state.result or "bust"

    while hand_value(round_state.dealer_hand) < 17:
        used = round_state.player_hand + round_state.dealer_hand
        available_cards = [card for card in create_deck() if card not in used]
        round_state.dealer_hand.append(random.choice(available_cards))

    player_value = hand_value(round_state.player_hand)
    dealer_value = hand_value(round_state.dealer_hand)
    if is_bust(round_state.dealer_hand) or player_value > dealer_value:
        result = "win"
    elif player_value < dealer_value:
        result = "lose"
    else:
        result = "draw"

    round_state.finished = True
    round_state.result = result
    return result