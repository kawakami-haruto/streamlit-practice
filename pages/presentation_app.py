import streamlit as st

from models.presentation_app_backend import (
    Round,
    card_label,
    finish_round,
    hand_value,
    hit,
    start_round,
)


MAX_ROUNDS = 5
STARTING_BALANCE = 1000


def reset_game() -> None:
    for key in ("round_state", "round_number", "balance", "game_over", "celebrated"):
        st.session_state.pop(key, None)


st.set_page_config(page_title="ブラックジャック", page_icon="🃏")
st.title("🃏 ブラックジャック")
st.caption("ヒットとスタンドだけで遊ぶ、最大5回のミニゲームです。")

if "balance" not in st.session_state:
    st.session_state.balance = STARTING_BALANCE
    st.session_state.round_number = 0
    st.session_state.game_over = False
    st.session_state.celebrated = False

if st.session_state.game_over:
    if st.session_state.celebrated:
        st.balloons()
        st.success("5回連続でバーストしませんでした！おめでとうございます！")
    elif st.session_state.balance <= 0:
        st.error("所持金がなくなったため、ゲーム終了です。")
    else:
        st.error("バーストしたため、ゲーム終了です。")
    st.metric("最終残高", f"{st.session_state.balance}円")
    if st.button("最初から遊ぶ", type="primary"):
        reset_game()
        st.rerun()
    st.stop()

if "round_state" not in st.session_state:
    st.subheader(f"ラウンド {st.session_state.round_number + 1} / {MAX_ROUNDS}")
    st.metric("残高", f"{st.session_state.balance}円")
    bet = st.number_input(
        "掛け金（1円〜所持金全額）",
        min_value=1,
        max_value=st.session_state.balance,
        value=min(10, st.session_state.balance),
        step=1,
    )
    if st.button("ゲーム開始", type="primary"):
        st.session_state.round_state = start_round(int(bet), st.session_state.balance)
        st.rerun()
    st.stop()


round_state: Round = st.session_state.round_state
st.subheader(f"ラウンド {st.session_state.round_number + 1} / {MAX_ROUNDS}")
st.write(f"掛け金: **{round_state.bet}円**　|　残高: **{st.session_state.balance}円**")

st.markdown("**ディーラーの手札**")
if round_state.finished and round_state.result != "bust":
    st.write("　".join(card_label(card) for card in round_state.dealer_hand))
    st.write(f"合計: {hand_value(round_state.dealer_hand)}")
else:
    st.write(f"{card_label(round_state.dealer_hand[0])}　🂠")

st.markdown("**あなたの手札**")
st.write("　".join(card_label(card) for card in round_state.player_hand))
st.write(f"合計: {hand_value(round_state.player_hand)}")

if not round_state.finished:
    hit_col, stand_col = st.columns(2)
    with hit_col:
        if st.button("ヒット", use_container_width=True):
            hit(round_state)
            st.rerun()
    with stand_col:
        if st.button("スタンド", use_container_width=True):
            finish_round(round_state)
            st.rerun()
else:
    result_messages = {
        "win": ("勝ち！", st.success),
        "lose": ("負け…", st.error),
        "draw": ("引き分け！", st.info),
        "bust": ("バースト！", st.error),
    }
    message, show_message = result_messages[round_state.result or "bust"]
    show_message(message)
    if not round_state.settled:
        if round_state.result == "bust":
            st.session_state.game_over = True
        elif round_state.result == "win":
            st.session_state.balance += round_state.bet
        elif round_state.result == "lose":
            st.session_state.balance -= round_state.bet
        round_state.settled = True
        if st.session_state.balance <= 0:
            st.session_state.game_over = True

    if round_state.result != "bust":
        st.write(f"このラウンド後の残高: {st.session_state.balance}円")
        if st.session_state.round_number + 1 >= MAX_ROUNDS and st.session_state.balance > 0:
            st.session_state.game_over = True
            st.session_state.celebrated = True
        elif not st.session_state.game_over and st.button("次のゲームへ", type="primary"):
            st.session_state.round_number += 1
            st.session_state.pop("round_state")
            st.rerun()

    if st.session_state.game_over and st.button("最初から遊ぶ", type="primary"):
        reset_game()
        st.rerun()
