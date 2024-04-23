
import streamlit as st

st.set_page_config(page_title = "Calculadora de Dieta Ideal")
st.title("Calculadora de Dieta Ideal")
st.subheader("Esse programa utiliza conceitos de nutrição, saúde e otimização para a criação de uma dieta ideal para você.")

with st.container():
  st.write("---")

sexo = st.number_input("Insira o seu sexo:")
st.write("1 para masculino e 2 para feminino")

peso = st.number_input("Insira o seu peso em kg:")

altura = st.number_input("Insira a sua altura em cm:")

idade = st.number_input("Insira a sua idade:")

atividade_fisica = st.number_input("Escolha entre as opções a sua frequência de atividade física")
st.write("1 - sedentário, 2 - levemente ativo, 3 - moderadamente ativo, 4 - muito ativo, 5 - super ativo")
