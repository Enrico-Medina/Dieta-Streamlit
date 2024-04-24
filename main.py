pip install transformers
import streamlit as st
import pandas as pd
from transformers import pipeline

# Dataframe Raw
df_nutricional = pd.read_excel("df_nutricional_classified (1).xlsx")

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
st.write("1 - Sedentário, 2 - Levemente ativo, 3 - Moderadamente ativo, 4 - Muito ativo, 5 - Super ativo")
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

resultados_nutrientes = calcular_nutrientes(sexo, peso, altura, idade, atividade_fisica)

if st.button('Calcular Nutrientes'):
    resultado_df = pd.DataFrame([resultados_nutrientes])

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

    # Criando um Dict com todas as variáveis linkadas ao ID que serão utilizadas no modelo
alimentos = {}

for index, row in df_nutricional.iterrows():
    id_alimento = row['id']

    valores_nutricionais = {
        'descricao': row['description'],
        'categoria': row['category'],
        'energia_kcal': row['energy_kcal'],
        'proteinas_g': row['protein_g'],
        'lipidios_g': row['lipids_g'],
        'carboidratos_g': row['carbohydrates_g'],
        'calcio_mg': row['calcium_mg'],
        'magnesio_mg': row['magnesium_mg'],
        'zinco_mg': row['zinc_mg'],
        'refeicao_do_dia' : row['meal_of_the_day']
    }
    alimentos[id_alimento] = valores_nutricionais

from ortools.linear_solver import pywraplp

# Configuração inicial do Solver
solver = pywraplp.Solver.CreateSolver('GLOP')

if not solver:
    print('Solver GLOP não disponível.')
else:
    # Criando as variáveis de quantidade.
    quantidade = {alimento: solver.NumVar(0, solver.infinity(), f'Quantidade_{alimento}') for alimento in alimentos.keys()}
    # Criando as variáveis de quantidade mínima de alimentos (variabilidade)
    selecao_alimento = {alimento: solver.BoolVar(f'Selecao_{alimento}') for alimento in alimentos.keys()}
    # Criando as variáveis de quantidade mínima de categorias (variabilidade)
    categorias = set(dados['categoria'] for alimento, dados in alimentos.items())
    selecao_categoria = {categoria: solver.BoolVar(f'Selecao_{categoria}') for categoria in categorias}

    # Restrições
    # Refeição: Restringindo a quantidade de calorias por refeição do dia
    calorias_refeicao = {
        'breakfast': solver.Sum([quantidade[alimento] * dados['energia_kcal'] for alimento, dados in alimentos.items() if 'breakfast' in dados['refeicao_do_dia'].split(', ')]),
        'lunch': solver.Sum([quantidade[alimento] * dados['energia_kcal'] for alimento, dados in alimentos.items() if 'lunch' in dados['refeicao_do_dia'].split(', ')]),
        'dinner': solver.Sum([quantidade[alimento] * dados['energia_kcal'] for alimento, dados in alimentos.items() if 'dinner' in dados['refeicao_do_dia'].split(', ')])
    }

    # Macro-Nutrientes: Restringindo a quantidade de macro-nutrientes
    solver.Add(solver.Sum([quantidade[alimento] * dados['energia_kcal'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['tmb'])
    solver.Add(solver.Sum([quantidade[alimento] * dados['lipidios_g'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['fats'])
    solver.Add(solver.Sum([quantidade[alimento] * dados['carboidratos_g'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['carbs'])
    solver.Add(solver.Sum([quantidade[alimento] * dados['calcio_mg'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['calcium'])
    solver.Add(solver.Sum([quantidade[alimento] * dados['magnesio_mg'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['magnesium'])
    solver.Add(solver.Sum([quantidade[alimento] * dados['zinco_mg'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['zinc'])
    solver.Add(solver.Sum([quantidade[alimento] * dados['proteinas_g'] for alimento, dados in alimentos.items()]) <= resultados_nutrientes['prot'])

    # Quantidade de alimentos: Restringindo a quantidade mínima de alimentos (variabilidade)
    for alimento in alimentos.keys():
        solver.Add(quantidade[alimento] >= selecao_alimento[alimento] * 1)  # Limite inferior

    solver.Add(solver.Sum(selecao_alimento.values()) >= 10)  # Número mínimo de alimentos selecionados

    # Categorias: Restringindo a quantidade mínima de categorias (variabilidade)
    for categoria in categorias:
        alimentos_da_categoria = [alimento for alimento, dados in alimentos.items() if dados['categoria'] == categoria]
        solver.Add(solver.Sum([selecao_alimento[alimento] for alimento in alimentos_da_categoria]) >= selecao_categoria[categoria])
        solver.Add(selecao_categoria[categoria] >= 1)  # Pelo menos uma categoria selecionada

    # Refeições: Restringindo o TMB baseado nas calorias por refeição
    solver.Add(calorias_refeicao['breakfast'] <= 1 * resultados_nutrientes['tmb'] / 3)
    solver.Add(calorias_refeicao['lunch'] <= 1 * resultados_nutrientes['tmb'] / 3)
    solver.Add(calorias_refeicao['dinner'] <= 1 * resultados_nutrientes['tmb'] / 3)

status = solver.Solve()

if st.button('Calcular refeições'):

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        st.success('Solução encontrada (ótima ou viável):')
        refeicoes = ['breakfast', 'lunch', 'dinner']
        for refeicao in refeicoes:
            st.subheader(f"Refeição: {refeicao.capitalize()}")
            results = []
            for alimento, dados in alimentos.items():
                if refeicao in dados['refeicao_do_dia'].split(', ') and quantidade[alimento].solution_value() > 0:
                    descricao = dados['descricao']
                    quantidade_alimento = round(quantidade[alimento].solution_value(), 2)
                    results.append(f"{descricao}: {quantidade_alimento} unidades")
            if results:
                st.write('\n'.join(results))
            else:
                st.write("Nenhum alimento selecionado para esta refeição.")
            st.write("---")  # A linha separadora para cada refeição

    elif status == pywraplp.Solver.INFEASIBLE:
        st.error('O problema é inviável.')

    elif status == pywraplp.Solver.UNBOUNDED:
        st.error('O problema é ilimitado.')

    else:
        st.warning('Nenhuma solução ótima ou viável foi encontrada.')
