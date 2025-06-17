# app.py

import streamlit as st
import pandas as pd
from data_processing import carregar_dados # Importa a função do outro arquivo
from visualizations import plotar_mapa, plotar_acidentes_por_hora, plotar_top_causas, exibir_dados_detalhados # Importa as funções de visualização
import logging

# ==============================================================================
# 1. Configuração de Logs
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E CARREGAMENTO DOS DADOS
# ==============================================================================
st.set_page_config(layout="wide", page_title="Dashboard de Acidentes de Trânsito", page_icon="🚗")

df_acidentes = carregar_dados()

# ==============================================================================
# 3. INTERFACE DO DASHBOARD E LÓGICA DOS FILTROS
# ==============================================================================
if df_acidentes is not None:
    st.sidebar.header("Filtros Interativos")
    logging.info("Dashboard iniciado e dados carregados com sucesso.")

    # Filtro por Estado (UF)
    lista_ufs = sorted(df_acidentes['uf'].unique())
    uf_selecionada = st.sidebar.multiselect(
        'Selecione o Estado (UF):',
        options=lista_ufs,
        default=lista_ufs
    )
    
    # --- CORREÇÃO: Lógica mais robusta para ordenar e selecionar os meses ---
    # Lista mestra de meses na ordem correta
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Pega os meses que realmente existem nos dados
    meses_nos_dados = df_acidentes['mes'].unique()
    
    # Ordena os meses disponíveis de acordo com a lista mestra
    meses_disponiveis = sorted(meses_nos_dados, key=lambda m: ordem_meses.index(m))
    
    mes_selecionado = st.sidebar.multiselect(
        "Selecione o Mês:",
        options=meses_disponiveis,
        default=meses_disponiveis # Garante que todos os meses disponíveis comecem selecionados
    )

    # Filtro por Causa do Acidente
    lista_causas = ['TODAS'] + sorted(df_acidentes['causa_acidente'].unique())
    causa_selecionada = st.sidebar.selectbox(
        'Selecione a Causa do Acidente:',
        options=lista_causas
    )

    # --- APLICAÇÃO DOS FILTROS ---
    # Começa com uma cópia do dataframe original (já filtrado para 6 meses)
    df_filtrado = df_acidentes.copy()

    # Aplica os filtros. Se uma seleção estiver vazia, o filtro não é aplicado.
    if uf_selecionada:
        df_filtrado = df_filtrado[df_filtrado['uf'].isin(uf_selecionada)]
    
    # ALTERAÇÃO: Garante que o filtro de mês só seja aplicado se a seleção não estiver vazia
    # Se 'mes_selecionado' estiver vazio, nenhum filtro de mês é aplicado, mostrando todos os dados disponíveis.
    if mes_selecionado:
        df_filtrado = df_filtrado[df_filtrado['mes'].isin(mes_selecionado)]

    if causa_selecionada != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['causa_acidente'] == causa_selecionada]
    
    logging.info(f"Dados filtrados. Total de registros após filtros: {len(df_filtrado)}")

    # --- Título e Métricas ---
    st.title("Dashboard de Análise de Acidentes de Trânsito 🚗")
    st.markdown("Análise dos **últimos 6 meses** de dados. Use os filtros para explorar.")

    st.markdown("### Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    total_acidentes = df_filtrado.shape[0]
    total_mortos = df_filtrado['mortos'].sum()
    taxa_mortalidade = (total_mortos / total_acidentes) * 100 if total_acidentes > 0 else 0

    col1.metric("Total de Acidentes", f"{total_acidentes:,}".replace(",", "."))
    col2.metric("Total de Vítimas Fatais", f"{total_mortos:,}".replace(",", "."))
    col3.metric("Mortalidade (%)", f"{taxa_mortalidade:.2f}%")
    logging.info(f"Métricas calculadas: Acidentes={total_acidentes}, Mortos={total_mortos}, Taxa Mortalidade={taxa_mortalidade:.2f}%")


    # --- Chamadas das Funções de Visualização ---
    col_mapa, col_vazio = st.columns([2, 1]) # Cria colunas para o mapa não ocupar a tela toda
    with col_mapa:
        plotar_mapa(df_filtrado)

    st.markdown("---")

    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        plotar_acidentes_por_hora(df_filtrado)
            
    with col_graf2:
        plotar_top_causas(df_filtrado)
            
    # --- Exibição dos Dados Detalhados ---
    exibir_dados_detalhados(df_filtrado)

else:
    st.error("Não foi possível carregar os dados. Verifique o arquivo de origem.")