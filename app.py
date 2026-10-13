import streamlit as st

st.title("Hello, Streamlit!")
st.write("これはStreamlitアプリケーションのサンプルです。")

number_one = st.number_input("数値を入力してください:", value=0)
number_two = st.number_input("もう一つの数値を入力してください:", value=0)

st.write(f"入力された数字の積は: {number_one * number_two} です。")