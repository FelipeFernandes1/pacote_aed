# -*- coding: utf-8 -*-
"""Pacote_AED.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YtJz7xYpyzoQX56XTHtetbhwqnGnIYI-
"""

import pandas as pd
import seaborn as sns
sns.set_palette("deep")
import matplotlib.pyplot as plt
import math
import numpy as np
import statsmodels.api as sm

#FUNÇÃO PARA REALIZAR A ANÁLISE UNIVARIADA
def univariada(coluna):
  """Está é um função para analisar uma variável por vez. 
A análise leverá em conta se a variável é nominal, ordinal, discreta ou contínua,
porém é necessário fazer o devido tratamento para que todas variáveis qualitativas
sejam do tipo 'object'
  """
  if coluna.dtype == 'object':
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
        # Plotando gráficos de barra
        plt.figure(figsize=(5, 3))
        sns.barplot(x=tabela['frequencia_relativa'], y=tabela[variavel], edgecolor='black', palette='deep')
        plt.xlabel('frequencia_relativa')
        plt.ylabel(variavel)
        plt.tight_layout()
        plt.show()
    else:
        print('GRÁFICO DE PIZZA')
        # Definindo uma paleta de cores personalizada
        plt.figure(figsize=(3, 3))
        plt.pie(tabela['frequencia_relativa'], labels=tabela[variavel], autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.show()
  else:
      # Analisando as medidas estatísticas
      print(f'''MEDIDAS ESTATÍSTICAS

{coluna.describe()}

CONTAGEM DE VALORES NULOS/AUSENTES
{len(coluna)-coluna.count()}''')
      print('')
      print('HISTOGRAMA E BOXPLOT')
      # Definindo a paleta de cores globalmente
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

#FUNÇÃO PARA REALIZAR A ANÁLISE BIVARIADA
def bivariada(explicativa, resposta, faixas=0):
  """Esta é uma função que analisa a correlação/associação entre uma variável explicativa e uma variável resposta.
A técnicas utilizadas são Person, IV e R², a depender dos tipos de variáveis.
Primeiro argumento informar a variável explicativa.
Segundo argumento informar a variável resposta(Se for binária precisa ser do tipo int e conter os valores 0/1).
Terceiro argumento facultativo"""

#Calculando a correlação de Person
  if len(explicativa.unique()) > 2 and explicativa.dtype != 'object' and len(resposta.unique()) > 2:
    #calculando a correlação
    correlacao = round(explicativa.corr(resposta), 2)
    #classificando
    benchmark = ''
    if correlacao <= -0.7:
      benchmark = 'FORTEMENTE NEGATIVA'
    elif correlacao <= 0.6:
      benchmark = 'FRACA'
    else:
      benchmark = 'FORTEMENTE POSITIVA'
    print(f"A CORRELAÇÃO DE PERSON É: {correlacao}")
    print(f'CLASSIFICAÇÃO: {benchmark}')
    print('')
    #Plotando o gráfico de dispersão
    cor_deep = sns.color_palette('deep')[0] 
    plt.figure(figsize=(4, 3))
    sns.scatterplot(x=explicativa, y=resposta, color=cor_deep)
    plt.xlabel(explicativa.name)
    plt.ylabel(resposta.name)
    plt.show()

#Calculando o information value
  elif len(resposta.unique()) == 2:
    #Criando faixas se a variável for numérica
    numerica = ''
    if type(explicativa) != str and explicativa.nunique() > 15:
      explicativa_num = explicativa #fazendo uma cópia da variável para o bloxplot
      if faixas != 0:
        explicativa = pd.cut(explicativa, bins=faixas)
        explicativa = explicativa.astype(str)
      else:
        faixas = 1 + int(math.log2(len(explicativa)))
        explicativa = pd.cut(explicativa, bins=faixas)
        explicativa = explicativa.astype(str)
      numerica = 'Sim'
  #Criando a tabela IV
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
    df_iv = df_iv.sort_values(by='Taxa_Valor_Um')
    df_iv = df_iv.drop(columns=['Freq_absoluta','Freq_relativa','Valor_Um_relativo','Valor_Zero_relativo'])
    soma_iv = round(df_iv['IV'].sum(), 2)
  #classificando
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
    #organizando a tabela
    df_iv2 = df_iv.reset_index()
    #Printando a tabela IV e o resultado
    print('TABELA IV')
    print('')
    print(df_iv)
    print(f'''
O INFORMATION VALUE TOTAL É: {soma_iv}
CLASSIFICAÇÃO: {benchmark}''')
  #printando o gráfico
    print('')
    if numerica == 'Sim':
      plt.figure(figsize=(4, 3))
      sns.boxplot(x=resposta, y=explicativa_num, palette='deep')
      plt.xlabel(resposta.name)
      plt.ylabel(explicativa.name)
      plt.tight_layout()
      plt.show()
    elif numerica != 'Sim': 
      plt.figure(figsize=(5, 3))
      sns.barplot(x=df_iv2.iloc[:,3], y=df_iv2.iloc[:,0].astype(str), edgecolor='black', palette='deep')
      plt.xlabel('Taxa_Valor_Um')
      plt.ylabel(df_iv2.iloc[:,0].name)
      plt.tight_layout()
      plt.show()

#Calculando o coeficiente de determinação(R²)
  elif len(resposta.unique()) > 2 and ((len(explicativa.unique()) == 2 or explicativa.dtype == 'object')):
    #Codificando a variável qualitativa e calculando o R²
    df_reg = pd.get_dummies(explicativa, drop_first=True)
    variavel_dummie = sm.add_constant(df_reg)
    modelo = sm.OLS(resposta, variavel_dummie).fit() #Cria um modelo de regressão linear simples
    r_squared = round(modelo.rsquared, 2) #Extrai o R²
    #classificando
    benchmark = ''
    if r_squared <= 0.25:
      benchmark = 'FRACO'
    elif r_squared < 0.5:
      benchmark = 'MÉDIO'
    elif r_squared < 0.75:
      benchmark = 'FORTE'
    else:
      benchmark = 'MUITO FORTE'
  #Printando
    print(f'''O COEFICIENTE DE DETERMINAÇÃO(R²) É: {r_squared}
  CLASSIFICAÇÃO: {benchmark}''')
    print('')
    plt.figure(figsize=(len(explicativa.unique())+2, 3))
    sns.boxplot(x=explicativa, y=resposta, palette='deep')
    plt.xlabel(explicativa.name)
    plt.ylabel(resposta.name)
    plt.tight_layout()
    plt.show()
      
#FUNÇÃO PARA IDENTIFICAR OS ÍNDICES DOS OUTLIERS EM REFERÊNCIA A UMA VARIÁVEL RESPOSTA BINÁRIA
def outliers(explicativa, resposta):
    """Está é uma função que retorna os índices considerados outliers em relação a uma variável binária.
    É necessário atribuir o retorno a uma variável, para obter os ídices.
    primeiro argumento > variável explicativa
    segundo argumento > variável resposta"""
    outliers_indices = []

    for classe in range(2): 
        explicativa_classe = explicativa[resposta == classe]
        Q1 = np.percentile(explicativa_classe, 25)
        Q3 = np.percentile(explicativa_classe, 75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        outliers_indices_classe = np.where((resposta == classe) & ((explicativa_classe < limite_inferior) | (explicativa_classe > limite_superior)))
        outliers_indices.extend(outliers_indices_classe[0])

    return outliers_indices

#FUNÇÃO PARA CONSTRUIR UM RANKING DE ASSOCIAÇÃO/CORRELAÇÃO ENTRE AS VARIÁVEIS EXPLICATIVAS E A VARIÁVEL RESPOSTA
def ranking(df, resposta, faixas=0):
  """Esta função retorna uma tabela com um ranking de associação/correlação.
  primeiro argumento > dataframe
  segundo argumento > variável resposta(Se for binária precisa ser do tipo int e conter os valores 0/1).
  terceiro argumento > faixas(facultativo)"""
  #criando uma cópia do df para não alterar o original
  df_funcao = df.copy()
  #criando as listas para armazenar os resulados
  valor = []
  tecnica = []
  variavel = []
  classificacao = []
  #Iterando entre todas colunas e a variável resposta
  for explicativa in df_funcao.columns:
    #Calculando a correlação de Person
    if len(df_funcao[explicativa].unique()) > 2 and df_funcao[explicativa].dtype != 'object' and len(resposta.unique()) > 2:
      #calculando a correlação
      correlacao = round(df_funcao[explicativa].corr(resposta), 2)
      #classificando
      benchmark = ''
      if correlacao <= -0.7:
        benchmark = 'FORTE'
      elif correlacao <= 0.6:
        benchmark = 'FRACO'
      else:
        benchmark = 'FORTE'
      #armazenando o resultado
      variavel.append(explicativa)
      tecnica.append('Person')
      valor.append(correlacao)
      classificacao.append(benchmark)
    #Calculando o information value
    elif len(resposta.unique()) == 2:
      #Criando faixas se a variável for numérica
      numerica = ''
      if type(df_funcao[explicativa]) != str and df_funcao[explicativa].nunique() > 15:
        if faixas != 0:
          df_funcao[explicativa] = pd.cut(df_funcao[explicativa], bins=faixas)
          df_funcao[explicativa] = df_funcao[explicativa].astype(str)
        else:
          faixas = 1 + int(math.log2(len(df[explicativa])))
          df_funcao[explicativa] = pd.cut(df_funcao[explicativa], bins=faixas)
          df_funcao[explicativa] = df_funcao[explicativa].astype(str)
        numerica = 'Sim'
    #Criando a tabela IV
      df_iv = pd.crosstab(df_funcao[explicativa], resposta)
      variavel_resposta = resposta.name
      df_iv['Freq_absoluta'] = df_iv[1] + df_iv[0]
      df_iv['Freq_relativa'] = df_iv['Freq_absoluta']/df_iv['Freq_absoluta'].sum()
      df_iv['Valor_Um_relativo'] = (df_iv[1]/df_iv[1].sum())
      df_iv['Valor_Zero_relativo'] = (df_iv[0]/df_iv[0].sum())
      df_iv['Taxa_Valor_Um'] = (df_iv[1]/df_iv['Freq_absoluta'])
      df_iv['Odds'] = df_iv['Valor_Um_relativo']/df_iv['Valor_Zero_relativo']
      df_iv['IV'] = (df_iv['Valor_Um_relativo']-df_iv['Valor_Zero_relativo'])* np.log(df_iv['Odds'])
      df_iv['IV'].replace(np.inf, 0, inplace=True)
      df_iv = df_iv.sort_values(by='Taxa_Valor_Um')
      df_iv = df_iv.drop(columns=['Freq_absoluta','Freq_relativa','Valor_Um_relativo','Valor_Zero_relativo'])
      soma_iv = round(df_iv['IV'].sum(), 2)
    #classificando
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
      #armazenando o resultado
      variavel.append(explicativa)
      tecnica.append('IV')
      valor.append(soma_iv)
      classificacao.append(benchmark)
    #Calculando o coeficiente de determinação(R²)
    elif len(resposta.unique()) > 2 and ((len(df_funcao[explicativa].unique()) == 2 or df_funcao[explicativa].dtype == 'object')):
      #Codificando a variável qualitativa e calculando o R²
      df_reg = pd.get_dummies(df_funcao[explicativa], drop_first=True)
      variavel_dummie = sm.add_constant(df_reg)
      modelo = sm.OLS(resposta, variavel_dummie).fit() #Cria um modelo de regressão linear simples
      r_squared = round(modelo.rsquared, 2) #Extrai o R²
      #classificando
      benchmark = ''
      if r_squared <= 0.25:
        benchmark = 'FRACO'
      elif r_squared < 0.5:
        benchmark = 'MÉDIO'
      elif r_squared < 0.75:
        benchmark = 'FORTE'
      else:
        benchmark = 'MUITO FORTE'
    #armazenando o resultado
      variavel.append(explicativa)
      tecnica.append('R²')
      valor.append(r_squared)
      classificacao.append(benchmark)
  #Printando o ranking
  df_ranking = pd.DataFrame({'Posição':'' ,
                            'Variável': variavel,
                             'Valor': valor,
                             'Classificação': classificacao,
                             'Técnica': tecnica})
  ordem = {'MUITO FORTE': 1, 'FORTE': 2, 'MÉDIO': 3, 'FRACO': 4, 'MUITO FRACO': 5}
  df_ranking['Posição'] = df_ranking['Classificação'].map(ordem)
  df_ranking = df_ranking.sort_values(by=['Posição','Valor'], ascending=[True, False])
  df_ranking.drop(columns=['Posição'], inplace=True)
  df_ranking.reset_index(inplace=True, drop=True)
  return df_ranking

#FUNÇÃO PARA REALIZAR ANÁLISE COMBINATÓRIA
def combinatoria(elementos, posicoes, ordem_importa, tem_repeticao):
  """Função para calcular a análise combinatória, sendo permutação, arranjo ou combinação.
  É útil para utilizar na probabilidade clássica.
  n > número de elementos possíveis
  r > número de posições
  ordem_importa > 'sim'/'nao' indica se a ordem das disposições importa
  repeticao = 'sim'/'nao' indica se pode haver repetição dos elementos"""
  if tem_repeticao == 'nao':
    if ordem_importa != "sim": #combinação sem repetição
      resultado = math.factorial(elementos) / (math.factorial(posicoes) * math.factorial(elementos - posicoes))
      print(f'O resultado é {int(resultado)} combinações possíveis.')
    elif elementos == posicoes: #permutação sem repetição
      resultado = math.factorial(elementos)
      print(f'O resultado é {int(resultado)} permutações possíveis.')
    else: #arranjo sem repetição
      resultado = math.factorial(elementos) / math.factorial(elementos - posicoes)
      print(f'O resultado é {int(resultado)} arranjos possíveis.')
  else:
    if ordem_importa != "sim": #combinação com repetição
      resultado = math.comb(elementos + posicoes - 1, posicoes)
      print(f'O resultado é {int(resultado)} combinações possíveis, com repetição.')
    elif elementos == posicoes: #permutação com repetição
      resultado = elementos ** posicoes
      print(f'O resultado é {int(resultado)} permutações possíveis, com repetição.')
    else:#arranjo com repetição
      resultado = elementos ** posicoes
      print(f'O resultado é {int(resultado)} arranjos possíveis, com repetição.')
