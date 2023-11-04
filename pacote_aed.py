# -*- coding: utf-8 -*-
"""Pacote_AED.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YtJz7xYpyzoQX56XTHtetbhwqnGnIYI-
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math
import numpy as np
import statsmodels.api as sm

#Função para analisar variáveis qualitativas
def qualitativa(coluna):
  #temas
  minha_paleta = ['royalblue','skyblue','lightsteelblue', 'cornflowerblue']
  sns.set_palette(minha_paleta)

  #Tabela de frequencia
  tabela = coluna.value_counts().reset_index()
  nome_coluna = tabela.columns[1]
  tabela = tabela.rename(columns={nome_coluna: 'frequencia_absoluta'})
  tabela = tabela.rename(columns={'index': nome_coluna})
  tabela['frequencia_relativa'] = tabela['frequencia_absoluta']/tabela['frequencia_absoluta'].sum()
  tabela['frequencia_acumulada'] = tabela['frequencia_relativa'].cumsum()
  variavel = tabela.columns[0]
  print('TABELA DE FREQUÊNCIA')
  print(' ')
  print(tabela.to_string(index=False))
  print(' ')

  #verificando valores nulos/ausentes
  print(f'''CONTAGEM DE VALORES NULOS/AUSENTES
{len(coluna)-coluna.count()}''')
  print(' ')

  if len(coluna.value_counts()) > 3:
    print('GRÁFICO DE BARRAS')
    #Plotando gráficos de barra
    plt.figure(figsize=(5, 3))
    sns.barplot(x=tabela[variavel], y=tabela['frequencia_relativa'], palette=minha_paleta , edgecolor='black')
    plt.xlabel(variavel)
    plt.ylabel('frequencia_relativa')
    plt.tight_layout()
    plt.show()
  else:
    print('GRÁFICO DE PIZZA')
    plt.figure(figsize=(3, 3))
    plt.pie(tabela['frequencia_relativa'], labels=tabela[variavel], autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.show()

#Função para analisar variáveis quantitativas
def quantitativa(coluna):
  #temas
  minha_paleta = ['royalblue','skyblue','lightsteelblue', 'cornflowerblue']
  sns.set_palette(minha_paleta)

  #Analisando as medidas estatísticas
  print(f'''MEDIDAS ESTATÍSTICAS

  {coluna.describe()}

CONTAGEM DE VALORES NULOS/AUSENTES
  {len(coluna)-coluna.count()}''')
  print('')

  print('HISTOGRAMA E BOXPLOT')
  # Plotando histograma e boxplot
  num_bins = 1 + int(math.log2(len(coluna))) # Calculando o número de bins usando a regra de Sturges
  fig, axes = plt.subplots(1, 2, figsize=(6, 3))
  sns.histplot(x=coluna, bins=num_bins, kde=False, ax=axes[0])
  axes[0].set_ylabel('Frequência absoluta')
  axes[0].set_xlabel(coluna.name)
  sns.boxplot(y=coluna, ax=axes[1])
  axes[1].set_xlabel(coluna.name)
  axes[1].set_ylabel('')
  plt.tight_layout()
  plt.show()

#Criando a função para calcular o Information Value
def tabela_iv(explicativa, resposta):

  if type(explicativa) != str and explicativa.nunique() > 15:
    num_bins = 1 + int(math.log2(len(explicativa)))
    explicativa = pd.cut(explicativa, bins=num_bins)
    explicativa = explicativa.astype(str)

  df_iv = pd.crosstab(explicativa, resposta)
  variavel_resposta = resposta.name
  df_iv['Freq_absoluta'] = df_iv[1] + df_iv[0]
  df_iv['Freq_relativa'] = df_iv['Freq_absoluta']/df_iv['Freq_absoluta'].sum()
  df_iv['Valor_Um_relativo'] = (df_iv[1]/df_iv[1].sum())
  df_iv['Valor_Zero_relativo'] = (df_iv[0]/df_iv[0].sum())
  df_iv['Taxa_Valor_Um'] = (df_iv[1]/df_iv['Freq_absoluta'])
  df_iv['Odds'] = df_iv['Valor_Um_relativo']/df_iv['Valor_Zero_relativo']
  df_iv['IV'] = (df_iv['Valor_Um_relativo']-df_iv['Valor_Zero_relativo'])* np.log(df_iv['Odds'])
  df_iv['IV'].replace(np.inf, 0, inplace=True)
  df_iv = df_iv.drop(columns=['Freq_absoluta','Freq_relativa','Valor_Um_relativo','Valor_Zero_relativo'])
  soma_iv = round(df_iv['IV'].sum(), 2)

  benchmark = ''
  if soma_iv <= 0.02:
     benchmark = 'MUITO FRACO'
  elif soma_iv < 0.1:
    benchmark = 'FRACO'
  elif soma_iv < 0.3:
    benchmark = 'MÉDIO'
  elif soma_iv < 0.5:
    benchmark = 'FORTE'
  else:
    benchmark = 'MUITO FORTE'

  return print(df_iv),print(f'''
O INFORMATION VALUE TOTAL É: {soma_iv}
CLASSIFICADO COMO: {benchmark}''')

#Criando função para calcular o coeficiente de determinação
def r_quadrado(qualitativa, quantitativa):

  #temas
  minha_paleta = ['royalblue','skyblue','lightsteelblue', 'cornflowerblue']
  sns.set_palette(minha_paleta)

  variavel_dummie = sm.add_constant(qualitativa)
  modelo = sm.OLS(quantitativa, variavel_dummie).fit() #Cria um modelo de regressão linear simples
  r_squared = round(modelo.rsquared, 2) #Extrai o R²

  benchmark = ''
  if r_squared <= 0.25:
     benchmark = 'FRACO'
  elif r_squared < 0.5:
    benchmark = 'MÉDIO'
  elif r_squared < 0.75:
    benchmark = 'FORTE'
  else:
    benchmark = 'MUITO FORTE'

  print(f'''O COEFICIENTE DE DETERMINAÇÃO(R²) É: {r_squared}
CLASSIFICADO COMO: {benchmark}''')
  plt.figure(figsize=(4, 3))
  sns.boxplot(x=qualitativa, y=quantitativa)
  plt.xlabel(qualitativa.name)
  plt.ylabel(quantitativa.name)
  plt.tight_layout()
  plt.show()

#Função para calcular a correlação de Person
def person(variavel_A, variavel_B):
  correlacao = round(variavel_A.corr(variavel_B), 2)

  benchmark = ''
  if correlacao <= -0.7:
     benchmark = 'FORTEMENTE NEGATIVA'
  elif correlacao <= 0.6:
    benchmark = 'FRACA'
  else:
    benchmark = 'FORTEMENTE POSITIVA'

  print(f"A CORRELAÇÃO DE PERSON ENTRE {variavel_A.name.upper()} E {variavel_B.name.upper()} É: {correlacao}")
  print(f'CLASSIFICAÇÃO: {benchmark}')
  print('')

  #Plotando o gráfico de dispersão
  plt.figure(figsize=(4, 3))
  sns.scatterplot(x=variavel_A, y=variavel_B)
  plt.xlabel(variavel_A.name)
  plt.ylabel(variavel_B.name)
  plt.show()
