# Automação do IGR – CASSI × Autogestões

Script em Python que baixa os dados abertos da ANS, calcula o **Índice Geral de Reclamações (IGR)** da CASSI e da média das operadoras de autogestão, mês a mês, e gera automaticamente um relatório em Excel.

O que seria um processo manual de vários passos (baixar arquivos, filtrar, somar, calcular e montar a planilha) roda com **um único comando, em cerca de 30 segundos**, sempre do mesmo jeito.

Este projeto complementa o meu dashboard em Power BI *"Panorama da CASSI frente às autogestões"*: o dashboard faz a análise, e este script automatiza a atualização de um dos indicadores.

---

## O que o script faz

O fluxo segue o padrão **ETL** (extrair, transformar, carregar):

1. **Extrai:** baixa dois arquivos direto do [Portal de Dados Abertos da ANS](https://dadosabertos.ans.gov.br/FTP/PDA/)
   - `Relatorio_cadop.csv`: cadastro das operadoras ativas e a modalidade de cada uma
   - `pda-023-igr.csv`: reclamações e beneficiários por operadora, por mês
2. **Transforma:**
   - mantém apenas planos de **assistência médica**
   - identifica a **CASSI** (registro ANS 346659) e todas as operadoras de **autogestão**
   - calcula o **IGR médio das autogestões** para cada mês
   - coloca CASSI e autogestões lado a lado e calcula a diferença entre elas
3. **Carrega:** salva um arquivo Excel datado (ex.: `relatorio_igr_cassi_2026-09-29.xlsx`) na mesma pasta do script. Cada execução gera um relatório novo, sem apagar os anteriores.

---

## Como o IGR é calculado e por quê

O IGR mede **quantas reclamações uma operadora recebe na ANS para cada 100 mil beneficiários**. Quanto menor, melhor.

```
IGR = reclamações ÷ beneficiários × 100.000
```

Exemplo, com a CASSI em ago/2026: 347 ÷ 530.063 × 100.000 = **65,46**

- **Por que dividir pelos beneficiários?** Para comparar operadoras de tamanhos diferentes. Em número absoluto, uma operadora grande sempre recebe mais reclamações, só por ter mais clientes.
- **Por que multiplicar por 100.000?** Para deixar o número legível. É a escala oficial usada pela ANS.
- **Por que o script calcula a média das autogestões?** A ANS publica o IGR de cada operadora, mas não o de um grupo. O script **soma as reclamações** de todas as autogestões, **soma os beneficiários** de todas e só depois divide. Assim, cada operadora pesa conforme o seu tamanho (média ponderada).

| Operadora | Reclamações | Beneficiários | IGR |
|---|---|---|---|
| A (grande) | 500 | 1.000.000 | 50 |
| B (pequena) | 2 | 1.000 | 200 |
| **Grupo (soma ÷ soma)** | **502** | **1.001.000** | **50,1** |

A média simples dos dois índices daria 125, distorcida por uma operadora com apenas mil beneficiários.

---

## Resultado

Exemplo das primeiras linhas do relatório gerado:

| COMPETENCIA | QTD_BENEFICIARIOS | IGR_CASSI | IGR_AUTOGESTOES | DIFERENCA |
|---|---|---|---|---|
| 2026-08 | 530.063 | 65,46 | 51,98 | 13,48 |
| 2026-07 | 530.063 | 66,60 | 57,03 | 9,57 |
| 2026-06 | 531.835 | 58,10 | 50,95 | 7,15 |

![Relatório gerado](print_relatorio.png)

**Validação:** os valores gerados pelo script são idênticos aos calculados no dashboard em Power BI, feito de forma independente com os mesmos dados.

---

## Como executar

**Requisitos:** Python 3.10 ou superior

```bash
# 1. Instalar as bibliotecas
pip install pandas openpyxl

# 2. Executar o script
python relatorio_igr.py
```

O Excel é criado na mesma pasta do script.

### Execução automática (opcional)

O script pode ser agendado pelo **Agendador de Tarefas do Windows** para rodar sozinho, por exemplo toda semana:

- **Programa:** caminho do `python.exe`
- **Argumento:** caminho do `relatorio_igr.py`

Como o script salva o arquivo usando a própria pasta como referência (`Path(__file__).parent`), ele funciona corretamente mesmo quando executado pelo agendador.

---

## Decisões técnicas

- **`dtype={"REGISTRO_OPERADORA": str}`:** o registro ANS é um código, não uma quantidade. Lido como texto, ele mantém os zeros à esquerda (ex.: `000515`), que seriam perdidos se lido como número.
- **`sep=";"` e `decimal=","`:** os arquivos da ANS seguem o padrão brasileiro, com ponto e vírgula entre as colunas e vírgula decimal.
- **`low_memory=False`:** faz o pandas ler o arquivo inteiro antes de definir os tipos das colunas, evitando avisos de tipos mistos.
- **Nome do arquivo com a data:** mantém o histórico de execuções sem sobrescrever relatórios anteriores.

---

## Tecnologias

- Python 3
- pandas: leitura, filtragem e cálculo
- openpyxl: geração do arquivo Excel

---

## Limitações

- O IGR mostra **quanto** os beneficiários reclamam, não **por que** reclamam. Entender as causas exigiria dados internos.
- O script depende da estrutura dos arquivos publicados pela ANS. Se a ANS mudar nomes de colunas ou endereços, o código precisará de ajuste.

---

## Autor

**Gustavo Henrique Santos**
[LinkedIn](https://www.linkedin.com/in/gustavo-hs-santos)

Projeto independente, desenvolvido exclusivamente com dados públicos da ANS, sem vínculo com a CASSI.
