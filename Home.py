import streamlit as st
import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')

def login():
    st.title("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = user
            st.success("Logged in!")
        else:
            st.error("Invalid login")

def signup():
    st.title("📝 Signup")
    new_user = st.text_input("New Username")
    new_pwd = st.text_input("New Password", type="password")
    if st.button("Create Account"):
        c.execute("INSERT INTO users VALUES (?,?)", (new_user, new_pwd))
        conn.commit()
        st.success("Account created. Go to Login.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

tabs = st.tabs(["Login", "Signup"])
with tabs[0]:
    login()
with tabs[1]:
    signup()
