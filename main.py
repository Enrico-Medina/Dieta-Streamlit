import streamlit as st

st.set_page_config(page_title = "Calculadora de Dieta Ideal")
st.title("Calculadora de Dieta Ideal")
st.subheader("Esse programa utiliza conceitos de nutrição, saúde e otimização para a criação de uma dieta ideal para você.")

with st.container():
  st.write("---")

sexo = st.number_input("Insira o seu sexo:", min_value=1, max_value=2, value=0, format='%d')
st.write("1 para masculino e 2 para feminino")
st.write("---")

peso = st.number_input("Insira o seu peso em kg:", min_value=40, max_value=120, value=0, step=1, format='%d')
st.write("---")

altura = st.number_input("Insira a sua altura em cm:", min_value=120, max_value=200, value=0, step=1, format='%d')
st.write("---")

idade = st.number_input("Insira a sua idade:", min_value=14, max_value=90, value=0, step=1, format='%d')
st.write("---")

atividade_fisica = st.number_input("Escolha entre as opções a sua frequência de atividade física:", min_value=1, max_value=5, value= 2 step=1, format='%d')
st.write("1 - sedentário, 2 - levemente ativo, 3 - moderadamente ativo, 4 - muito ativo, 5 - super ativo")
st.write("---")


