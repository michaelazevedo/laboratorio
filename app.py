# rifa_app.py

import streamlit as st
import random
import json
import os

ARQUIVO_JSON = "rifas.json"
SENHA_AUTORIZACAO = "Xima1009el23"  # Altere para sua senha

# Função para carregar dados do arquivo JSON
def carregar_dados():
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r") as f:
            return json.load(f)
    return []

# Função para salvar dados no arquivo JSON
def salvar_dados(dados):
    with open(ARQUIVO_JSON, "w") as f:
        json.dump(dados, f, indent=4)

# Função para limpar dados
def limpar_dados():
    st.session_state.rifas = []
    salvar_dados([])
    st.success("✅ Todos os dados foram excluídos com sucesso!")

# Inicializa session_state com dados salvos
if 'rifas' not in st.session_state:
    dados_carregados = carregar_dados()
    for rifa in dados_carregados:
        if 'valor' not in rifa:
            rifa['valor'] = 10.0
    st.session_state.rifas = dados_carregados

# Calcula o total vendido
def calcular_total_vendido():
    return sum(rifa['valor'] for rifa in st.session_state.rifas if rifa['comprador'])

# Interface Streamlit
st.title("🎫 Sistema de Rifas")

# Configurações na barra lateral
st.sidebar.header("Configurações")
valor_padrao = st.sidebar.number_input("Valor Padrão da Rifa (R$)", min_value=0.0, value=10.0, step=1.0)

# Exibe o total vendido na barra lateral
total_vendido = calcular_total_vendido()
st.sidebar.metric("💰 Total Vendido", f"R$ {total_vendido:.2f}")

# Menu lateral
menu = st.sidebar.selectbox(
    "Escolha uma opção",
    ["Adicionar Número", "Adicionar Lote de Números", "Comprar Rifa", "Listar Rifas", "Sortear Rifa"],
    key="menu_principal"
)

# === MENU: Adicionar Número Único ===
if menu == "Adicionar Número":
    st.header("➕ Adicionar Número de Rifa")
    numero = st.number_input("Número da Rifa", min_value=1, step=1, value=1)
    valor = st.number_input("Valor desta Rifa (R$)", min_value=0.0, value=valor_padrao, step=1.0)
    if st.button("Adicionar"):
        for rifa in st.session_state.rifas:
            if rifa['numero'] == numero:
                st.warning("Número já cadastrado!")
                break
        else:
            st.session_state.rifas.append({
                'numero': numero,
                'comprador': None,
                'valor': float(valor)
            })
            salvar_dados(st.session_state.rifas)
            st.success(f"Número {numero} adicionado com sucesso!")

# === MENU: Adicionar Lote de Números ===
elif menu == "Adicionar Lote de Números":
    st.header("📦 Adicionar Lote de Números")
    col1, col2 = st.columns(2)
    inicio = col1.number_input("Número Inicial", min_value=1, value=1, step=1)
    fim = col2.number_input("Número Final", min_value=inicio + 1, value=250, step=1)
    valor_lote = st.number_input("Valor padrão das Rifas (R$)", min_value=0.0, value=valor_padrao, step=1.0)

    if st.button("Adicionar Todas as Rifas"):
        novas_rifas = []
        for num in range(inicio, fim + 1):
            # Verifica se o número já existe
            if any(rifa['numero'] == num for rifa in st.session_state.rifas):
                continue
            novas_rifas.append({
                'numero': num,
                'comprador': None,
                'valor': float(valor_lote)
            })

        if novas_rifas:
            st.session_state.rifas.extend(novas_rifas)
            salvar_dados(st.session_state.rifas)
            st.success(f"{len(novas_rifas)} novas rifas adicionadas com sucesso!")
        else:
            st.info("Nenhuma nova rifa foi adicionada. Todos os números já estão cadastrados.")

# === MENU: Comprar Rifa ===
elif menu == "Comprar Rifa":
    st.header("🛒 Comprar uma Rifa")
    numero = st.number_input("Número da Rifa", min_value=1, step=1, value=1)
    nome = st.text_input("Nome do Comprador")
    if st.button("Comprar"):
        if nome.strip() == "":
            st.warning("Por favor, insira um nome válido.")
        else:
            for rifa in st.session_state.rifas:
                if rifa['numero'] == numero:
                    if rifa['comprador']:
                        st.warning("Este número já foi comprado.")
                        break
                    rifa['comprador'] = nome
                    salvar_dados(st.session_state.rifas)
                    st.success(f"{nome} comprou a rifa número {numero}.")
                    break
            else:
                st.error("Número não encontrado.")

# === MENU: Listar Rifas ===
elif menu == "Listar Rifas":
    st.header("📋 Lista de Rifas")
    dados = []
    for rifa in st.session_state.rifas:
        status = "Disponível" if rifa['comprador'] is None else f"Comprada por {rifa['comprador']}"
        dados.append({
            "Número": rifa['numero'],
            "Status": status,
            "Valor (R$)": f"{rifa['valor']:.2f}"
        })
    st.table(dados)

# === MENU: Sortear Rifa ===
elif menu == "Sortear Rifa":
    st.header("🎁 Sortear Rifa")
    if st.button("Sortear Agora"):
        compradas = [rifa for rifa in st.session_state.rifas if rifa['comprador'] is not None]
        if not compradas:
            st.warning("Nenhuma rifa foi comprada ainda.")
        else:
            sorteada = random.choice(compradas)
            st.balloons()
            st.success(f"🎉 A rifa sorteada foi o número {sorteada['numero']}, comprada por {sorteada['comprador']}!")

# === BOTÃO PARA LIMPAR TODOS OS DADOS ===
with st.sidebar.expander("⚠️ Limpar Dados"):
    senha = st.text_input("Digite a senha de autorização", type="password")
    if st.button("Limpar Dados"):
        if senha == SENHA_AUTORIZACAO:
            limpar_dados()
        else:
            st.error("❌ Senha incorreta!")