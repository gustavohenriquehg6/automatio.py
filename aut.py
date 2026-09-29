import pandas as pd
from datetime import date

# 1. Links dos dados públicos da ANS
URL_OPERADORAS = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
URL_IGR = "https://dadosabertos.ans.gov.br/FTP/PDA/IGR/IGR_versao_2023/pda-023-igr.csv"
REGISTRO_CASSI = "346659"

# 2. Baixar os dados
print("Baixando dados da ANS...")
operadoras = pd.read_csv(URL_OPERADORAS, sep=";", dtype={"REGISTRO_OPERADORA": str})
igr = pd.read_csv(URL_IGR, sep=";", dtype={"REGISTRO_OPERADORA": str}, decimal=",")

# 3. Filtrar
igr = igr[igr["COBERTURA"] == "Assistência médica"]
lista_autogestoes = operadoras.loc[operadoras["MODALIDADE"] == "Autogestão", "REGISTRO_OPERADORA"]
igr_autogestoes = igr[igr["REGISTRO_OPERADORA"].isin(lista_autogestoes)]
igr_cassi = igr[igr["REGISTRO_OPERADORA"] == REGISTRO_CASSI]

# 4. Calcular o IGR médio ponderado das autogestões
media = igr_autogestoes.groupby("COMPETENCIA")[["QTD_RECLAMACOES", "QTD_BENEFICIARIOS"]].sum().reset_index()
media["IGR_AUTOGESTOES"] = (media["QTD_RECLAMACOES"] / media["QTD_BENEFICIARIOS"] * 100000).round(2)

cassi = igr_cassi[["COMPETENCIA", "QTD_BENEFICIARIOS", "QTD_RECLAMACOES", "IGR"]]
cassi = cassi.rename(columns={"IGR": "IGR_CASSI"})

relatorio = cassi.merge(media[["COMPETENCIA", "IGR_AUTOGESTOES"]], on="COMPETENCIA")
relatorio["DIFERENCA"] = (relatorio["IGR_CASSI"] - relatorio["IGR_AUTOGESTOES"]).round(2)
relatorio = relatorio.sort_values("COMPETENCIA", ascending=False)

# 5. Salvar em Excel
nome_arquivo = f"relatorio_igr_cassi_{date.today()}.xlsx"
relatorio.to_excel(nome_arquivo, index=False)
print(f"Relatório salvo: {nome_arquivo}")
print(relatorio.head())