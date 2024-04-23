import streamlit as st
import pandas as pd

st.set_page_config(page_title = "Calculadora de Dieta Ideal")
st.title("Calculadora de Dieta Ideal")
st.subheader("Esse programa utiliza conceitos de nutrição, saúde e otimização para a criação de uma dieta ideal para você.")

with st.container():
  st.write("---")

sexo = st.number_input("Insira o seu sexo:", min_value=1, max_value=2, value=1, format='%d')
st.write("1 para masculino e 2 para feminino")
st.write("---")

peso = st.number_input("Insira o seu peso em kg:", min_value=40, max_value=120, value=70, step=1, format='%d')
st.write("---")

altura = st.number_input("Insira a sua altura em cm:", min_value=120, max_value=200, value=170, step=1, format='%d')
st.write("---")

idade = st.number_input("Insira a sua idade:", min_value=14, max_value=90, value=30, step=1, format='%d')
st.write("---")

atividade_fisica = st.number_input("Escolha entre as opções a sua frequência de atividade física:", min_value=1, max_value=5, value= 2, step=1, format='%d')
st.write("1 - sedentário, 2 - levemente ativo, 3 - moderadamente ativo, 4 - muito ativo, 5 - super ativo")
st.write("---")

# Criando a função de TMB
def calcular_nutrientes(sexo, peso, altura, idade, atividade_fisica):
    # Equação de Mifflin-St Jeor
    tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) + (5 if sexo == 1 else -161)
    fatores_atividade = [1.2, 1.375, 1.55, 1.725, 1.9]
    tmb_ajustada = tmb_base * fatores_atividade[atividade_fisica - 1]
    if tmb_ajustada <= 1700:
      tmb_ajustada += 300

    # Dict com os macro-nutrientes ajustados baseado no TMB
    nutrientes = {
        'tmb': round(tmb_ajustada,2),
        'prot': round(tmb_ajustada * 0.25/4,2),
        'carbs': round(tmb_ajustada * 0.55/4,2),
        'fats': round(tmb_ajustada * 0.22/4,2),
        'calcium': 1000 if idade < 50 else 1200,
        'magnesium': 400,
        'zinc': 12
    }
    return nutrientes

if st.button('Calcular Nutrientes'):
    resultado = calcular_nutrientes(sexo, peso, altura, idade, atividade_fisica)
    resultado_df = pd.DataFrame([resultado])

    # Renomeando as colunas para a exibição no DataFrame
    resultado_df.rename(columns={
        'tmb': 'Taxa Metabólica Basal',
        'prot': 'Proteínas (g)',
        'carbs': 'Carboidratos (g)',
        'fats': 'Gorduras(g)',
        'calcium': 'Cálcio (mg)',
        'magnesium': 'Magnésio (mg)',
        'zinc': 'Zinco (mg)'
    }, inplace=True)
    st.write("Resultado:")
    st.table(resultado_df)
