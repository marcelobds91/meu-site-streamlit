import json
import os
import bcrypt
import streamlit as st

USERS_FILE = "users.json"

MASTER_USUARIO = "admin_master"
MASTER_SENHA = "SuperSenhaMaster123!"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def cadastrar_usuario(username, senha):
    users = load_users()
    if username in users:
        return False, "Usuário já existe"
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    save_users(users)
    return True, "Usuário cadastrado com sucesso"

def autenticar_usuario(username, senha):
    # Verifica se é o usuário master
    if username == MASTER_USUARIO and senha == MASTER_SENHA:
        return True
    
    users = load_users()
    if username not in users:
        return False
    hashed = users[username].encode()
    return bcrypt.checkpw(senha.encode(), hashed)

def login_form():
    with st.form("login_form"):
        st.subheader("🔐 Login")
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            if autenticar_usuario(username, senha):
                st.session_state["usuario_logado"] = username
                st.success(f"Bem-vindo, {username}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")

def cadastro_form():
    with st.form("cadastro_form"):
        st.subheader("📝 Cadastro")
        username = st.text_input("Novo usuário")
        senha = st.text_input("Nova senha", type="password")
        submit = st.form_submit_button("Cadastrar")
        if submit:
            ok, msg = cadastrar_usuario(username, senha)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

def logout():
    if st.session_state.get("usuario_logado"):
        st.session_state.pop("usuario_logado")
        st.success("Logout realizado com sucesso.")
        st.experimental_rerun()
