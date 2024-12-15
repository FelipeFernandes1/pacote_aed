# -*- coding: utf-8 -*-
"""funcoes.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18bVhnqtcb3BhbeSh_zjDaDfCjuocexXV
"""

import pandas as pd
import plotly.express as px
from scipy.stats import chi2_contingency
import numpy as np
from sklearn.metrics import cohen_kappa_score
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def qualitativa_quantitativa(df, target_variable, comparison_variables, target_type="categorical"):
    """
    Analisa a relação entre uma variável alvo (categórica ou numérica) e um conjunto de variáveis de comparação.
    Cria gráficos de boxplot com Plotly e calcula o índice eta (η²) e o R² para variáveis numéricas e categóricas.

    Parâmetros:
    - df: DataFrame pandas contendo os dados.
    - target_variable: Nome da variável alvo (pode ser categórica ou numérica).
    - comparison_variables: Lista de nomes das variáveis para comparação (categóricas ou numéricas).
    - target_type: Tipo da variável alvo ('categorical' ou 'numeric'). Padrão é 'categorical'.

    Retorno:
    - Nenhum. Exibe os gráficos e imprime os índices eta² e R².
    """
    if target_variable not in df.columns:
        raise ValueError(f"A variável '{target_variable}' não está no DataFrame.")

    if not all(var in df.columns for var in comparison_variables):
        raise ValueError("Uma ou mais variáveis especificadas não estão no DataFrame.")

    if target_type == "categorical":
        # Verificar se a variável alvo é categórica
        if not isinstance(df[target_variable].dtype, pd.CategoricalDtype) and \
           not pd.api.types.is_object_dtype(df[target_variable]):
            raise ValueError(f"A variável '{target_variable}' não é categórica.")

        # Converter para categórica, se necessário
        df[target_variable] = df[target_variable].astype("category")

        # Calcular eta² e R² para cada variável numérica
        eta_squared = {}
        r_squared = {}
        for num_var in comparison_variables:
            if not np.issubdtype(df[num_var].dtype, np.number):
                continue
            temp_df = df[[target_variable, num_var]].dropna()
            groups = temp_df.groupby(target_variable, observed=True)[num_var]
            overall_mean = temp_df[num_var].mean()

            # Variância entre os grupos
            ss_between = sum(groups.size() * (groups.mean() - overall_mean) ** 2)
            # Variância total
            ss_total = sum((temp_df[num_var] - overall_mean) ** 2)

            eta_squared[num_var] = ss_between / ss_total

            # Calcular R² (coeficiente de determinação)
            X = pd.get_dummies(temp_df[target_variable], drop_first=True)
            y = temp_df[num_var]
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            r_squared[num_var] = r2_score(y, y_pred)

        # Configuração de subplots: 4 gráficos por linha
        num_graphs = len(comparison_variables)
        rows = (num_graphs - 1) // 4 + 1  # Calcula o número de linhas necessárias
        cols = 4  # Quatro gráficos por linha

        # Criar subgráficos sem títulos
        fig = make_subplots(
            rows=rows, cols=cols, subplot_titles=[]  # Removendo os títulos dos subgráficos
        )

        # Adicionar gráficos
        for idx, num_var in enumerate(comparison_variables):
            if not np.issubdtype(df[num_var].dtype, np.number):
                continue
            temp_df = df[[target_variable, num_var]].dropna()
            row = idx // cols + 1
            col = idx % cols + 1

            boxplot = go.Box(
                x=temp_df[target_variable],
                y=temp_df[num_var],
            )
            fig.add_trace(boxplot, row=row, col=col)

            fig.update_yaxes(title_text=num_var, row=row, col=col)

        # Layout final
        fig.update_layout(
            height=300 * rows,  # Ajusta altura com base no número de linhas
            title_text=f"Gráficos de {target_variable} com variáveis numéricas",  # Título do gráfico
            showlegend=False,
            template="plotly_white"
        )
        fig.update_xaxes(title_text=target_variable)
        fig.show()

        # Exibir índices eta² e R²
        print("Índices Eta² e R² (Associação entre variável categórica e numéricas):")
        for var in eta_squared:
            print(f"{var}: Eta² = {eta_squared[var]}, R² = {r_squared[var]}")

    elif target_type == "numeric":
        # Para a variável numérica como alvo, calcular eta² com variáveis categóricas
        eta_squared = {}
        r_squared = {}
        for cat_var in comparison_variables:
            if isinstance(df[cat_var].dtype, pd.CategoricalDtype) or pd.api.types.is_object_dtype(df[cat_var]):
                temp_df = df[[target_variable, cat_var]].dropna()
                groups = temp_df.groupby(cat_var, observed=True)[target_variable]
                overall_mean = temp_df[target_variable].mean()

                # Variância entre os grupos
                ss_between = sum(groups.size() * (groups.mean() - overall_mean) ** 2)
                # Variância total
                ss_total = sum((temp_df[target_variable] - overall_mean) ** 2)

                eta_squared[cat_var] = ss_between / ss_total

                # Calcular R² (coeficiente de determinação)
                X = pd.get_dummies(temp_df[cat_var], drop_first=True)
                y = temp_df[target_variable]
                model = LinearRegression()
                model.fit(X, y)
                y_pred = model.predict(X)
                r_squared[cat_var] = r2_score(y, y_pred)

        # Configuração de subplots: 4 gráficos por linha
        num_graphs = len(comparison_variables)
        rows = (num_graphs - 1) // 4 + 1  # Calcula o número de linhas necessárias
        cols = 4  # Quatro gráficos por linha

        # Criar subgráficos sem títulos
        fig = make_subplots(
            rows=rows, cols=cols, subplot_titles=[]  # Removendo os títulos dos subgráficos
        )

        # Adicionar gráficos
        for idx, cat_var in enumerate(comparison_variables):
            if not (isinstance(df[cat_var].dtype, pd.CategoricalDtype) or pd.api.types.is_object_dtype(df[cat_var])):
                continue
            temp_df = df[[target_variable, cat_var]].dropna()
            row = idx // cols + 1
            col = idx % cols + 1

            boxplot = go.Box(
                x=temp_df[cat_var],
                y=temp_df[target_variable]
            )
            fig.add_trace(boxplot, row=row, col=col)

            fig.update_xaxes(title_text=cat_var, row=row, col=col)

        # Layout final
        fig.update_layout(
            height=300 * rows,  # Ajusta altura com base no número de linhas
            title_text=f"Gráficos de {target_variable} com variáveis categóricas",  # Título do gráfico
            showlegend=False,
            template="plotly_white"
        )
        fig.update_yaxes(title_text=target_variable)  # Adiciona nome da variável no eixo Y
        fig.show()

        # Exibir índices eta² e R²
        print("Índices Eta² e R² (Associação entre variável numérica e categóricas):")
        for var in eta_squared:
            print(f"{var}: Eta² = {eta_squared[var]}, R² = {r_squared[var]}")

    else:
        raise ValueError("O parâmetro 'target_type' deve ser 'categorical' ou 'numeric'.")
        
def quantitativa(df, target_variable, variables_to_compare):
    """
    Analisa a correlação entre uma variável alvo e um conjunto de variáveis específicas,
    exibindo as correlações de Pearson e Spearman.
    Remove valores faltantes apenas para as comparações realizadas, sem modificar o DataFrame original.

    Parâmetros:
    - df: DataFrame pandas contendo os dados.
    - target_variable: Nome da variável alvo.
    - variables_to_compare: Lista de nomes das variáveis a serem comparadas com a variável alvo.

    Retorno:
    - Nenhum. Exibe os gráficos de dispersão organizados e imprime as correlações.
    """
    if target_variable not in df.columns:
        raise ValueError(f"A variável '{target_variable}' não está no DataFrame.")

    if not all(var in df.columns for var in variables_to_compare):
        raise ValueError("Uma ou mais variáveis especificadas não estão no DataFrame.")

    # Selecionar apenas variáveis numéricas entre as especificadas
    numeric_df = df.select_dtypes(include='number')
    variables_to_compare = [var for var in variables_to_compare if var in numeric_df.columns]

    if target_variable not in numeric_df.columns:
        raise ValueError(f"A variável '{target_variable}' não é numérica.")

    correlations_pearson = {}
    correlations_spearman = {}
    num_vars = len(variables_to_compare)
    num_cols = 4  # Número de colunas no layout
    num_rows = -(-num_vars // num_cols)  # Cálculo do número de linhas (arredondamento para cima)

    # Criar subplots
    fig = make_subplots(
        rows=num_rows, cols=num_cols,
    )

    # Gerar gráficos de dispersão e adicionar às subplots
    for i, var in enumerate(variables_to_compare):
        row = i // num_cols + 1
        col = i % num_cols + 1

        # Remover valores faltantes antes de calcular correlação
        temp_df = numeric_df[[target_variable, var]].dropna()

        # Correlação de Pearson
        corr_pearson = temp_df[target_variable].corr(temp_df[var])
        correlations_pearson[var] = corr_pearson

        # Correlação de Spearman
        corr_spearman = temp_df[target_variable].corr(temp_df[var], method='spearman')
        correlations_spearman[var] = corr_spearman

        scatter = go.Scatter(
            x=temp_df[var],
            y=temp_df[target_variable],
            mode='markers',
            marker=dict(size=6),
            name=f"{var}",
        )
        fig.add_trace(scatter, row=row, col=col)

        # Atualizar o eixo X para cada gráfico com o nome da variável
        fig.update_xaxes(title_text=var, row=row, col=col)
        # Atualizar o eixo Y para todos os gráficos com a variável alvo
        fig.update_yaxes(title_text=target_variable, row=row, col=col)

    # Atualizar layout geral
    fig.update_layout(
        height=300 * num_rows,  # Ajustar altura do gráfico
        width=1200,  # Largura fixa
        title_text=f"Análise de Correlação com {target_variable}",
        showlegend=False,
        template="plotly_white"
    )

    # Mostrar gráfico
    fig.show()

    # Exibir índices de correlação
    print("Índices de Correlação de Pearson (linear):")
    for var, corr in correlations_pearson.items():
        print(f"{var}: {corr:.2f}")

    print("\nÍndices de Correlação de Spearman (não linear):")
    for var, corr in correlations_spearman.items():
        print(f"{var}: {corr:.2f}")

def qualitativa(df, var1, var2, normalize='none', cramers_v=True, chi2_test=True, cohen_kappa=True, handle_missing='drop'):
    """
    Gera um mapa de calor interativo e opcionalmente calcula o V de Cramér, o Teste Qui-Quadrado e o Kappa de Cohen
    para medir a associação entre var1 e várias variáveis de var2.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo os dados.
    - var1 (str): Nome da primeira variável categórica (eixo X).
    - var2 (list of str): Lista de nomes das variáveis categóricas para comparar com var1 (eixo Y).
    - normalize (str): Normalização dos dados ('none', 'all', 'index', 'columns').
    - cramers_v (bool): Se True, calcula e exibe o V de Cramér para cada comparação.
    - chi2_test (bool): Se True, realiza o Teste Qui-Quadrado entre as variáveis.
    - cohen_kappa (bool): Se True, calcula o Kappa de Cohen entre as variáveis.
    - handle_missing (str): Estratégia para lidar com valores ausentes ('drop', 'fill'). 
                            'drop' remove as linhas com valores ausentes, 'fill' substitui os valores ausentes por 'Desconhecido'.

    Retorna:
    - Nada. Exibe o gráfico para cada variável de var2 e imprime as métricas de associação (se solicitado).
    """
    
    # Verifica se as colunas existem no DataFrame
    if var1 not in df.columns:
        raise ValueError("A coluna var1 especificada não existe no DataFrame.")

    if not all(v in df.columns for v in var2):
        raise ValueError("Uma ou mais colunas em var2 não existem no DataFrame.")

    for v in var2:
        # Cria uma cópia do DataFrame original para cada iteração
        df_temp = df.copy()

        # Tratar valores ausentes conforme a estratégia definida
        if handle_missing == 'drop':
            df_temp = df_temp.dropna(subset=[var1, v])
        elif handle_missing == 'fill':
            df_temp[var1] = df_temp[var1].fillna('Desconhecido')
            df_temp[v] = df_temp[v].fillna('Desconhecido')
        
        # Cria a tabela de contingência
        contingency_table = pd.crosstab(df_temp[v], df_temp[var1], normalize=normalize if normalize != 'none' else False)

        # Calcula o V de Cramér, se solicitado
        if cramers_v:
            absolute_table = pd.crosstab(df_temp[v], df_temp[var1])  # Tabela não normalizada
            chi2, _, _, _ = chi2_contingency(absolute_table)
            n = absolute_table.values.sum()
            r, k = absolute_table.shape
            v_cramer = np.sqrt(chi2 / (n * (min(r, k) - 1)))
            print(f"V de Cramér entre {var1} e {v}: {v_cramer:.2f}")

            # Interpretação do V de Cramér
            if v_cramer < 0.10:
                interpretation = "Associação muito fraca ou nenhuma associação"
            elif v_cramer < 0.20:
                interpretation = "Associação fraca"
            elif v_cramer < 0.30:
                interpretation = "Associação moderada"
            else:
                interpretation = "Associação forte"

            print(f"Interpretação para {v}: {interpretation}\n")

        # Realiza o Teste Qui-Quadrado, se solicitado
        if chi2_test:
            chi2_stat, p_val, dof, expected = chi2_contingency(pd.crosstab(df_temp[v], df_temp[var1]))
            print(f"Teste Qui-Quadrado entre {var1} e {v}: Estatística Qui-Quadrado = {chi2_stat:.2f}, p-valor = {p_val:.4f}")

            if p_val < 0.05:
                print(f"Hipótese rejeitada: Existe associação significativa entre {var1} e {v}.\n")
            else:
                print(f"Hipótese não rejeitada: Não existe associação significativa entre {var1} e {v}.\n")

        # Calcula o Kappa de Cohen, se solicitado
        if cohen_kappa:
            kappa = cohen_kappa_score(df_temp[var1], df_temp[v])
            print(f"Kappa de Cohen entre {var1} e {v}: {kappa:.2f}")
            if kappa < 0.20:
                print("Interpretação: Concordância muito fraca ou nenhuma concordância.")
            elif kappa < 0.40:
                print("Interpretação: Concordância fraca.")
            elif kappa < 0.60:
                print("Interpretação: Concordância moderada.")
            elif kappa < 0.80:
                print("Interpretação: Concordância forte.")
            else:
                print("Interpretação: Concordância excelente.\n")

        # Gera o heatmap com Plotly
        fig = px.imshow(
            contingency_table,
            labels=dict(x=var1, y=v, color='Frequência'),
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            title=f"Mapa de Calor entre {var1} e {v} (Normalização: {normalize})",
            xaxis_title=var1,
            yaxis_title=v
        )
        fig.show()





