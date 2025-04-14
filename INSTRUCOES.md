## **Aplicação - Inserção de Pareceres**

### **Objetivo**
Aplicação desktop leve em Python com interface gráfica (PyQt), para **agilizar o processo de geração de linha digitável do boleto** do sistema interno WBA, conectando diretamente ao banco de dados SQL Server (RDS AWS).

---

### **Arquitetura da aplicação**

#### 1. **Camadas**
- `db.py` → Conexão e execução de queries no SQL Server.
- `models.py` → Classes Cedente, Bordero e Titulos com lógica de dados.
- `ui.py` → Interface com Tkinter (busca, exibição, inserção).
- `main.py` → Inicialização da aplicação.

---

### **Funcionalidades**

#### Busca de Cedente ou Sacado
- Campo de busca por **nome, CNPJ (`cgc`) ou código interno**.
- Sugestões em tempo real com `Listbox` conforme usuário digita.
- Consulta:
```sql
SELECT TOP(5) id, codigo, nome, cgc, tipo
FROM sigcad
WHERE tipo = 'Cedente' OR tipo = 'Sacado' AND (
    nome LIKE '%<termo>%'
    OR cgc LIKE '%<termo>%'
    OR codigo LIKE '%<termo>%'
)
ORDER BY nome;
```

---

#### Exibição de Títulos
Habilitar campos de filtro de títulos após selecionar um Cedente.
- Campo de busca por **empresa** (empresa = `SEC|FIDC`).
- Campo de busca por **bordero** (ex: `bordero = <bordero>`).
- Campo de busca por **data do bordero** (ex: `BETWEEN <data_bordero_inicial> AND <data_bordero_final>`).
- Campo de busca por **data de vencimento** (ex: `BETWEEN <data_vencimento_inicial> AND <data_vencimento_final>`).


```sql
-- Dados do FIDC
SELECT
  f.id,
  'FIDC' AS empresa,
  f.clifor AS codigo,
  f.sacado,
  f.bordero,
  CAST(f.dtbordero AS DATE) AS data_bordero,
  f.dcto AS numero_documento,
  fidc.numero_port AS seu_numero,
  f.codigo codigo_dcto,
  f.tipodcto,
  CAST(fidc.[data] AS DATE) AS vencimento,
  fidc.valor

FROM sigfls AS f
INNER JOIN sigfidc AS fidc
  ON fidc.sigfls = f.ctrl_id
WHERE f.codigo IN ('040')
  AND (fidc.banco IS NULL OR LTRIM(RTRIM(fidc.banco)) = '')
  AND NOT(fidc.numero_port IS NULL OR LTRIM(RTRIM(fidc.numero_port)) = '')
  AND NOT EXISTS (
    SELECT 1 FROM sigfcs AS fcs WHERE fcs.sigfls = f.ctrl_id
  )
  AND f.clifor = <codigo_cedente>
  AND f.sacado = <codigo_sacado>
  AND f.bordero = <bordero>
  AND CAST(f.dtbordero AS DATE) BETWEEN <data_bordero_inicial> AND <data_bordero_final>
  AND CAST(fidc.vcto_ AS DATE) BETWEEN <data_vencimento_inicial> AND <data_vencimento_final>

UNION ALL

-- Dados do SEC
SELECT
  f.id,
  'SEC' AS empresa,
  f.clifor AS codigo,
  f.sacado,
  f.bordero,
  CAST(f.dtbordero AS DATE) AS data_bordero,
  f.dcto AS numero_documento,
  sec.numero_port AS seu_numero,
  f.codigo codigo_dcto,
  f.tipodcto,
  CAST(sec.vcto_ AS DATE) AS vencimento,
  sec.valor

FROM sigfls AS f
INNER JOIN sigflu AS sec
  ON sec.sigfls = f.ctrl_id
WHERE f.codigo IN ('040')
  AND (sec.banco IS NULL OR LTRIM(RTRIM(sec.banco)) = '')
  AND NOT(sec.numero_port IS NULL OR LTRIM(RTRIM(sec.numero_port)) = '')
  AND NOT EXISTS (
    SELECT 1 FROM sigfcs AS fcs WHERE fcs.sigfls = f.ctrl_id
  )
  AND f.clifor = <codigo_cedente>
  AND f.sacado = <codigo_sacado>
  AND f.bordero = <bordero>
  AND CAST(f.dtbordero AS DATE) BETWEEN <data_bordero_inicial> AND <data_bordero_final>
  AND CAST(sec.vcto_ AS DATE) BETWEEN <data_vencimento_inicial> AND <data_vencimento_final>
```

---

### Estrutura de dados

```python
class Pessoa:
    id: int # AUTO-INCREMENT
    codigo: int
    nome: str
    cgc: str
    tipo: str  # sempre "Sacado" ou "Cedente"

class Titulo:
    id: int # AUTO-INCREMENT
    empresa: str # SEC ou FIDC
    codigo: int # relacionar com Pessoa tipo "Cedente"
    sacado: int # relacionar com Pessoa tipo "Sacado"
    bordero: int # Bordero
    data_bordero: datetime.date # Data do bordero
    numero_documento: str # Número do documento
    seu_numero: str # Seu número
    codigo_dcto: str # Código do documento
    tipodcto: str # Tipo do documento
    vencimento: datetime.date # Data de vencimento
    valor: float # Valor do título
```

---

### Segurança e boas práticas

- Conexão SQL com `pyodbc` usando `.env` + `python-dotenv`.
- Input sanitizado.
- Consulta assíncrona leve para evitar travar UI.

---

## PROMPT FINAL

```text
Crie uma aplicação desktop simples em Python com PyQt para inserir pareceres em um sistema interno que utiliza SQL Server hospedado na AWS (RDS). A aplicação se conecta diretamente ao banco de dados "wba".

Funcionalidades:

1. Campo de busca por Pessoas (tabela: sigcad), usando nome, cgc (CNPJ) ou código. Podendo filtrar registros por tipo = 'Cedente' ou 'Sacado'. A busca deve ser dinâmica (ao digitar) e mostrar sugestões em uma lista.
   - A consulta deve retornar os 5 primeiros registros que atendem ao filtro.
   - A consulta deve ser feita com base no tipo selecionado: 'Cedente' ou 'Sacado'.
   - A consulta deve ser feita com o seguinte SQL:
    ```sql
    SELECT TOP(5) id, codigo, nome, cgc, tipo
    FROM sigcad
    WHERE tipo = <selected_type>
    AND (nome LIKE '%' + <search_term> + '%' OR cgc LIKE '%' + <search_term> + '%' OR codigo = <search_term>)
    ORDER BY nome
    ```
   - A busca deve ser feita em tempo real, conforme o usuário digita no campo de busca.
   - O resultado deve ser exibido em uma lista (Listbox) para o usuário selecionar.

2. Ao selecionar uma Pessoa, mostrar seus dados (nome, cgc, código, tipo) e habilitar os campos de filtro de títulos (empresa, bordero, data do bordero, data de vencimento). O usuário poderá filtrar os títulos por:
   - Empresa: SEC ou FIDC
   - Bordero: número do bordero
   - Data do Bordero: entre duas datas (inicial e final)
   - Data de vencimento: entre duas datas (inicial e final)
   - A consulta deve ser feita com o seguinte SQL:
    ```sql
    -- Dados do FIDC
    SELECT
    f.id,
    'FIDC' AS empresa,
    f.clifor AS codigo,
    f.sacado,
    f.bordero,
    CAST(f.dtbordero AS DATE) AS data_bordero,
    f.dcto AS numero_documento,
    fidc.numero_port AS seu_numero,
    f.codigo codigo_dcto,
    f.tipodcto,
    CAST(fidc.[data] AS DATE) AS vencimento,
    fidc.valor

    FROM sigfls AS f
    INNER JOIN sigfidc AS fidc
    ON fidc.sigfls = f.ctrl_id
    WHERE f.codigo IN ('040')
    AND (fidc.banco IS NULL OR LTRIM(RTRIM(fidc.banco)) = '')
    AND NOT(fidc.numero_port IS NULL OR LTRIM(RTRIM(fidc.numero_port)) = '')
    AND NOT EXISTS (
        SELECT 1 FROM sigfcs AS fcs WHERE fcs.sigfls = f.ctrl_id
    )
    AND f.clifor = <codigo_cedente>
    AND f.sacado = <codigo_sacado>
    AND f.bordero = <bordero>
    AND CAST(f.dtbordero AS DATE) BETWEEN <data_bordero_inicial> AND <data_bordero_final>
    AND CAST(fidc.vcto_ AS DATE) BETWEEN <data_vencimento_inicial> AND <data_vencimento_final>

    UNION ALL

    -- Dados do SEC
    SELECT
    f.id,
    'SEC' AS empresa,
    f.clifor AS codigo,
    f.sacado,
    f.bordero,
    CAST(f.dtbordero AS DATE) AS data_bordero,
    f.dcto AS numero_documento,
    sec.numero_port AS seu_numero,
    f.codigo codigo_dcto,
    f.tipodcto,
    CAST(sec.vcto_ AS DATE) AS vencimento,
    sec.valor

    FROM sigfls AS f
    INNER JOIN sigflu AS sec
    ON sec.sigfls = f.ctrl_id
    WHERE f.codigo IN ('040')
    AND (sec.banco IS NULL OR LTRIM(RTRIM(sec.banco)) = '')
    AND NOT(sec.numero_port IS NULL OR LTRIM(RTRIM(sec.numero_port)) = '')
    AND NOT EXISTS (
        SELECT 1 FROM sigfcs AS fcs WHERE fcs.sigfls = f.ctrl_id
    )
    AND f.clifor = <codigo_cedente>
    AND f.sacado = <codigo_sacado>
    AND f.bordero = <bordero>
    AND CAST(f.dtbordero AS DATE) BETWEEN <data_bordero_inicial> AND <data_bordero_final>
    AND CAST(sec.vcto_ AS DATE) BETWEEN <data_vencimento_inicial> AND <data_vencimento_final>
    ```
   - Os resultados devem ser exibidos em uma tabela (TableView) com as colunas: empresa, código, sacado, bordero, data_bordero, numero_documento, seu_numero, codigo_dcto, tipodcto, vencimento e valor.

3. O usuário poderá selecionar os títulos desejados e gerar a linha digitável do boleto.
   - A linha digitável deve ser gerada com base nos dados do título selecionado.
   - O usuário poderá selecionar múltiplos títulos para gerar as linhas digitáveis de uma só vez.
   - A linha digitável deve ser exibida em um campo de texto (TextBox) para o usuário copiar.
   - A linha digitável deve ser gerada utilizando uma função específica que formate os dados do título de acordo com o padrão de linha digitável do boleto bancário.
   - O script para gerar a linha digitável deve se basear no exemplo funcional abaixo:
   ```python
   from datetime import datetime

    def modulo_10(num):
        soma = 0
        multiplicador = 2
        for n in reversed(num):
            produto = int(n) * multiplicador
            soma += sum(map(int, str(produto)))
            multiplicador = 1 if multiplicador == 2 else 2
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto

    def modulo_11(num):
        pesos = [2, 3, 4, 5, 6, 7, 8, 9]
        soma = 0
        for i, n in enumerate(reversed(num)):
            peso = pesos[i % len(pesos)]
            soma += int(n) * peso
        resto = soma % 11
        dac = 11 - resto
        return 1 if dac in [0, 1, 10, 11] else dac

    def gerar_linha_digitavel(vencimento, valor, carteira, nosso_numero, agencia, conta, dac_nosso_numero, dac_conta):
        banco = '341'
        moeda = '9'

        # Fator de vencimento: Base 03/07/2000 (fator 1000)
        venc_dt = datetime.strptime(vencimento, '%d/%m/%Y')
        base = datetime(2000, 7, 3)
        dias_decorridos = (venc_dt - base).days
        fator = str(dias_decorridos + 1000).zfill(4)
        fator_venc = fator if int(fator) <= 9999 else str(1000 + (int(fator) - 10000))

        # Valor formatado com 10 dígitos (sem vírgula ou ponto)
        valor_formatado = str(int(float(valor) * 100)).zfill(10)

        # Campo livre: Carteira (3) + Nosso Número (8) + DAC Nosso Número (1) +
        # Agência (4) + Conta (5) + DAC Conta (1) + "000"
        campo_livre = f"{carteira}{nosso_numero}{dac_nosso_numero}{agencia.zfill(4)}{conta.zfill(5)}{dac_conta}000"

        # Monta o código de barras sem o DAC (posição 5)
        # O formato é: Banco (3) + Moeda (1) + [DAC] + Fator de Vencimento (4) + Valor (10) + Campo Livre (25)
        # Colocamos temporariamente um marcador "X" no lugar do DAC
        codigo_barras = banco + moeda + 'X' + fator_venc + valor_formatado + campo_livre
        # 341 9 X 1049 0000187024 109 00001719 7 1704 26957 8 000
        
        dac_barras = str(modulo_11(codigo_barras.replace('X', '')))
        
        codigo_barras = codigo_barras.replace('X', dac_barras)

        # Montagem da linha digitável:
        # Campo 1: Posições 1-4 + Posições 20-24 (código de barras) e seu DAC (módulo 10)
        campo1 = codigo_barras[0:4] + codigo_barras[19:24]
        dac1 = str(modulo_10(campo1))
        campo1 = f"{campo1[:5]}.{campo1[5:]}{dac1}"

        # Campo 2: Posições 25-34 do código de barras e seu DAC (módulo 10)
        campo2 = codigo_barras[24:34]
        dac2 = str(modulo_10(campo2))
        campo2 = f"{campo2[:5]}.{campo2[5:]}{dac2}"

        # Campo 3: Posições 35-44 do código de barras e seu DAC (módulo 10)
        campo3 = codigo_barras[34:44]
        dac3 = str(modulo_10(campo3))
        campo3 = f"{campo3[:5]}.{campo3[5:]}{dac3}"

        # Campo 4: DAC do código de barras (já calculado)
        campo4 = dac_barras

        # Campo 5: Fator de vencimento + valor
        campo5 = fator_venc + valor_formatado

        return f"{campo1} {campo2} {campo3} {campo4} {campo5}"

    # Teste básico
    if __name__ == '__main__':
        vencimento = input("Data de vencimento (dd/mm/yyyy): ")
        valor = input("Valor do título (ex: 123.45): ")
        carteira = input("Carteira (3 dígitos): ")
        nosso_numero = input("Nosso Número (8 dígitos): ")
        dac_nosso_numero = input("DAC Nosso Número (1 dígito): ")
        agencia = input("Agência (até 4 dígitos): ")
        conta = input("Conta Corrente (até 5 dígitos): ")
        dac_conta = input("DAC Conta Corrente (1 dígito): ")

        linha = gerar_linha_digitavel(vencimento, valor, carteira, nosso_numero, agencia, conta, dac_nosso_numero, dac_conta)
        print("\nLinha Digitável:")
        print(linha)
   ```
   - Os valores de Banco, Moeda, Carteira, Agencia, Conta e DAC serão fixos (variáveis de ambiente .env) e visíveis na interface.

3. O usuário poderá gerar um arquivo .xls com as linhas digitáveis dos títulos selecionados.
  - Deve conter as colunas: empresa, cedente, sacado, bordero, data_bordero, numero_documento, seu_numero, tipodcto, vencimento, valor e linha digitável (gerada no script).
  - O arquivo deve ser gerado no formato compatível com Excel e deve permitir a edição das informações.
  - O usuário também poderá escolher o local onde o arquivo será salvo.
  - O arquivo deve ser gerado utilizando uma biblioteca como `pandas` e `openpyxl` para facilitar a manipulação e criação do arquivo Excel.
  - O usuário poderá também escolher o formato do arquivo (XLSX ou CSV) antes de gerar.

Requisitos técnicos:
- Linguagem: Python 3.10+
- Interface: PyQt
- Banco: SQL Server (via pyodbc)
- Variáveis de conexão devem ser lidas de um arquivo `.env` (use python-dotenv)
- Separe o código em módulos: `db.py`, `models.py`, `ui.py`, `main.py`
- Trate exceções e valide entradas
- Dê prioridade à fluidez de uso e simplicidade visual

Estrutura esperada no banco:

Tabela sigcad:
- id INT (AUTO-INCREMENT)
- codigo INT
- nome VARCHAR
- cgc VARCHAR
- tipo VARCHAR ('Cedente'|'Sacado')

Query titulos:
- id INT (AUTO-INCREMENT)
- empresa VARCHAR ('SEC'|'FIDC')
- codigo INT (relacionar com Pessoa tipo 'Cedente')
- sacado INT (relacionar com Pessoa tipo 'Sacado')
- bordero INT (Bordero)
- data_bordero DATE
- numero_documento VARCHAR
- seu_numero VARCHAR
- codigo_dcto VARCHAR
- tipodcto VARCHAR
- vencimento DATE
- valor DECIMAL(10, 2)


Monte o projeto com arquivos separados, código funcional e instruções para rodar localmente.
```