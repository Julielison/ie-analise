import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt

import numpy as np

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors

import matplotlib.pyplot as plt
import os


def exportar_pdf(resultados):

    doc = SimpleDocTemplate("relatorio_vendas.pdf")
    elements = []

    styles = getSampleStyleSheet()
    titulo_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Título principal
    elements.append(Paragraph("Relatório Executivo de Vendas", titulo_style))
    elements.append(Spacer(1, 0.5 * inch))

    
    for chave, df in resultados.items():

        # Título da seção
        elements.append(Paragraph(f"Análise {chave}", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Texto explicativo
        texto = gerar_descricao(df)
        elements.append(Paragraph(texto, normal_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Gerar gráfico temporário
        nome_img = f"grafico_{chave}.png"

        gerar_imagem_grafico(df, nome_img)

        elements.append(Image(nome_img, width=5.5 * inch, height=3.5 * inch))
        elements.append(PageBreak())

    doc.build(elements)

    print("PDF gerado com sucesso: relatorio_vendas.pdf")

def gerar_imagem_grafico(df, caminho):

    if df.empty:
        return False

    import matplotlib.pyplot as plt

    # Se tiver 3 colunas (cliente, cidade, vendas)
    if len(df.columns) == 3:
        df = df.sort_values(by=df.columns[2], ascending=False).head(15)
        labels = (df.iloc[:, 0].astype(str) + " - " + df.iloc[:, 1].astype(str)).tolist()
        valores = df.iloc[:, 2].tolist()
        
        plt.figure(figsize=(12, 8))
        plt.barh(labels, valores)
        plt.xlabel(df.columns[2].replace('_',' ').title())
        plt.ylabel("Cliente - Cidade")
        plt.gca().invert_yaxis()  # Maior valor no topo
    else:
        x = df.iloc[:, 0]
        y = df.iloc[:, 1]

        plt.figure(figsize=(10, 5))

        # Se for ano (temporal)
        if str(x.name).lower() in ["ano"]:
            plt.plot(x, y, marker='o')
        else:
            df = df.sort_values(by=df.columns[1], ascending=False)
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]
            plt.bar(x, y)

    if len(df.columns) != 3:
        plt.title(f"{y.name.replace('_',' ').title()} por {x.name.replace('_',' ').title()}")
        plt.xlabel(x.name.replace('_',' ').title())
        plt.ylabel(y.name.replace('_',' ').title())
        plt.xticks(rotation=45, ha='right')
        
        # Formatação numérica apenas para gráficos sem 3 colunas
        plt.gca().yaxis.set_major_formatter(
            plt.FuncFormatter(lambda val, _: f"{val:,.0f}")
        )
    else:
        plt.title("Total de Vendas por Cliente e Cidade")
        
        # Formatação numérica no eixo X (valores) para gráficos com 3 colunas
        plt.gca().xaxis.set_major_formatter(
            plt.FuncFormatter(lambda val, _: f"{val:,.0f}")
        )

    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.4)

    plt.savefig(caminho)
    plt.close()

    return True


def gerar_descricao(df):

    if df.empty:
        return "Não houve registros suficientes para gerar análise."

    x_col = df.columns[0]
    y_col = df.columns[1]

    # Força conversão para numérico
    df[y_col] = pd.to_numeric(df[y_col], errors='coerce')

    # Remove possíveis NaN gerados
    df = df.dropna(subset=[y_col])

    if df.empty:
        return "Os dados retornados não são numéricos para análise estatística."

    maior = df.loc[df[y_col].idxmax()]
    menor = df.loc[df[y_col].idxmin()]
    total = df[y_col].sum()
    media = df[y_col].mean()

    descricao = (
        f"O total acumulado foi de {total:,.0f}. "
        f"A média registrada foi de {media:,.0f}. "
        f"O maior valor foi observado em {maior[x_col]} "
        f"com {maior[y_col]:,.0f}. "
        f"O menor desempenho ocorreu em {menor[x_col]} "
        f"com {menor[y_col]:,.0f}."
    )

    return descricao


europe_alpha3 = np.array([
    "ALB", # Albânia
    "AND", # Andorra
    "AUT", # Áustria
    "BLR", # Bielorrússia
    "BEL", # Bélgica
    "BIH", # Bósnia e Herzegovina
    "BGR", # Bulgária
    "HRV", # Croácia
    "CYP", # Chipre
    "CZE", # República Tcheca
    "DNK", # Dinamarca
    "EST", # Estônia
    "FIN", # Finlândia
    "FRA", # França
    "DEU", # Alemanha
    "GRC", # Grécia
    "HUN", # Hungria
    "ISL", # Islândia
    "IRL", # Irlanda
    "ITA", # Itália
    "LVA", # Letônia
    "LTU", # Lituânia
    "LUX", # Luxemburgo
    "MLT", # Malta
    "MDA", # Moldávia
    "MCO", # Mônaco
    "MNE", # Montenegro
    "NLD", # Países Baixos
    "MKD", # Macedônia do Norte
    "NOR", # Noruega
    "POL", # Polônia
    "PRT", # Portugal
    "ROU", # Romênia
    "RUS", # Rússia
    "SMR", # San Marino
    "SRB", # Sérvia
    "SVK", # Eslováquia
    "SVN", # Eslovênia
    "ESP", # Espanha
    "SWE", # Suécia
    "CHE", # Suíça
    "UKR", # Ucrânia
    "GBR", # Reino Unido
    "VAT"  # Vaticano
])



def extrair(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo)
    return df


def normalizar_dados(df):
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df = df.dropna(how="all")
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    if "vendas" in df.columns:
        df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce")

    df = df.fillna(0)

    return df



def carregar_db(tabelas_dict):
    conn = sqlite3.connect(":memory:")
    for nome_tabela, df in tabelas_dict.items():
        df.to_sql(nome_tabela, conn, index=False, if_exists="replace")

    return conn


def plot_resultado(df):

    if df.empty:
        print("DataFrame vazio.")
        return

    x_col = df.columns[0]
    y_col = df.columns[-1]

    x_label = traduzir_coluna(x_col)
    y_label = traduzir_coluna(y_col)

    plt.figure()

    # Série temporal real
    if eh_serie_temporal(df, x_col):
        df_sorted = df.sort_values(by=x_col)
        plt.plot(df_sorted[x_col], df_sorted[y_col])
        plt.xlabel("Ano")
        plt.ylabel(y_label)

    # Caso cliente + cidade
    elif len(df.columns) > 2:
        df_plot = df.copy()
        df_plot["grupo"] = (
            df_plot.iloc[:, 0].astype(str) + " - " +
            df_plot.iloc[:, 1].astype(str)
        )
        df_sorted = df_plot.sort_values(by=y_col)
        plt.barh(df_sorted["grupo"], df_sorted[y_col])
        plt.xlabel(y_label)
        plt.ylabel("Cliente - Cidade")

    # Ranking
    elif len(df) > 5:
        df_sorted = df.sort_values(by=y_col)
        plt.barh(df_sorted[x_col], df_sorted[y_col])
        plt.xlabel(y_label)
        plt.ylabel(x_label)

    # Comparação simples
    else:
        plt.bar(df[x_col], df[y_col])
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)

    titulo = f"{y_label} por {x_label}"
    plt.title(titulo)

    plt.tight_layout()
    plt.show()



def executar_queries(conn, queries_dict):
    resultados = {}
    
    for nome, sql in queries_dict.items():
        print(f"Executando: {nome}")
        df = pd.read_sql_query(sql, conn)
        resultados[nome] = df
    
    return resultados


def visualizar_tabela(conn, nome_tabela, limite=5):
    query = f"SELECT * FROM {nome_tabela} LIMIT {limite}"
    df = pd.read_sql_query(query, conn)
    print(f"\nVisualização da tabela: {nome_tabela}")
    print(df)
    return df


def eh_serie_temporal(df, x_col):
    # Regra 1: nome exatamente "ano"
    if x_col.lower() == "ano":
        return True
    
    # Regra 2: valores parecem anos (4 dígitos numéricos)
    try:
        valores = pd.to_numeric(df[x_col])
        if valores.between(1900, 2100).all():
            return True
    except:
        pass

    return False


import matplotlib.pyplot as plt
import pandas as pd


def traduzir_coluna(nome_coluna):

    mapa = {
        "clientenome": "Cliente",
        "clientepaís": "País",
        "clientecidade": "Cidade",
        "categorianome": "Categoria",
        "transportadoranome": "Transportadora",
        "fornecedornome": "Fornecedor",
        "vendedornome": "Vendedor",
        "total_vendas": "Total de Vendas ($)",
        "vendastotal": "Total de Vendas ($)",
        "vendasanuais": "Vendas Anuais ($)",
        "margem": "Margem ($)",
        "margemdelucro": "Margem de Lucro ($)",
        "descontototaldado": "Total de Descontos ($)",
        "custototal": "Custo Total de Frete ($)",
        "ano": "Ano"
    }

    return mapa.get(nome_coluna.lower(), nome_coluna.replace("_", " ").title())


QUERIES = {

"1": """
SELECT 
    clientenome AS cliente,
    SUM(vendas) AS total_vendas
FROM vendas_globais
GROUP BY clientenome
ORDER BY total_vendas DESC
LIMIT 10
""",

"2": """
SELECT 
    clientepaís AS pais,
    SUM(vendas) AS total_vendas
FROM vendas_globais
GROUP BY clientepaís
ORDER BY total_vendas DESC
LIMIT 3
""",

"3": """
SELECT 
    categorianome AS categoria,
    SUM(vendas) AS total_vendas
FROM vendas_globais
WHERE clientepaís = 'Brazil'
GROUP BY categorianome
ORDER BY total_vendas DESC
""",

"4": """
SELECT 
    t.transportadoranome AS transportadora,
    SUM(v.frete) AS total_frete
FROM vendas_globais v
JOIN transportadoras t
    ON t.transportadoraid = v.transportadoraid
GROUP BY t.transportadoranome
ORDER BY total_frete DESC
""",

"5": """
SELECT 
    clientenome AS cliente,
    SUM(vendas) AS total_vendas
FROM vendas_globais
WHERE categorianome = 'Men´s Footwear'
AND clientepaís = 'Germany'
GROUP BY clientenome
ORDER BY total_vendas DESC
""",

"6": """
SELECT 
    v.vendedornome AS vendedor,
    SUM(vg.desconto) AS total_descontos
FROM vendas_globais vg
JOIN vendedores v 
    ON vg.vendedorid = v.vendedorid
WHERE vg.clientepaís = 'USA'
GROUP BY v.vendedornome
ORDER BY total_descontos DESC
""",

"7": """
SELECT 
    f.fornecedornome AS fornecedor,
    SUM(vg.margem_bruta) AS total_margem
FROM fornecedores f
JOIN vendas_globais vg
    ON f.fornecedorid = vg.fornecedorid
WHERE vg.categorianome = 'Womens wear'
GROUP BY f.fornecedornome
ORDER BY total_margem DESC
LIMIT 5
""",

"8": """
SELECT 
    strftime('%Y', data) AS ano,
    SUM(vendas) AS total_vendas
FROM vendas_globais
WHERE strftime('%Y', data) BETWEEN '2009' AND '2012'
GROUP BY ano
ORDER BY ano ASC
""",

"9": """
SELECT 
    clientenome AS cliente,
    clientecidade AS cidade,
    SUM(vendas) AS total_vendas
FROM vendas_globais
WHERE categorianome = 'Men´s Footwear'
AND strftime('%Y', data) = '2011'
GROUP BY clientenome, clientecidade
ORDER BY total_vendas DESC
""",

"10": """
SELECT 
    clientepaís AS pais,
    SUM(vendas) AS total_vendas
FROM vendas_globais
WHERE clientepaísid IN (
    'ALB','AND','AUT','BLR','BEL','BIH','BGR','HRV','CYP','CZE',
    'DNK','EST','FIN','FRA','DEU','GRC','HUN','ISL','IRL','ITA',
    'LVA','LTU','LUX','MLT','MDA','MCO','MNE','NLD','MKD','NOR',
    'POL','PRT','ROU','RUS','SMR','SRB','SVK','SVN','ESP','SWE',
    'CHE','UKR','GBR','VAT'
)
GROUP BY clientepaís
ORDER BY total_vendas DESC
"""
}

def main():
    fornecedores = normalizar_dados(extrair("Fornecedores.csv"))
    transportadoras = normalizar_dados(extrair("Transportadoras.csv"))
    vendas_globais = normalizar_dados(extrair("Vendas Globais.csv"))
    vendedores = normalizar_dados(extrair("Vendedores.csv"))

    tabelas = {
        "fornecedores": fornecedores,
        "transportadoras": transportadoras,
        "vendas_globais": vendas_globais,
        "vendedores": vendedores
    }

    conn = carregar_db(tabelas)
    resultados = executar_queries(conn, QUERIES)

    # Exibir resultado da consulta 9
    print("\n" + "="*80)
    print("RESULTADO DA CONSULTA 9:")
    print("="*80)
    print(resultados["9"].to_string(index=False))
    print("="*80)
    print(f"Total de clientes: {len(resultados['9'])}")
    print(f"Total de vendas: ${resultados['9']['total_vendas'].sum():,.2f}")
    print("="*80 + "\n")

    # for chave, df in resultados.items():
    #     plot_resultado(df)

    exportar_pdf(resultados)



if __name__ == "__main__":
    main()