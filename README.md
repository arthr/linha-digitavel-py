# Gerador de Linha Digitável - WBA

Aplicação desktop em Python com PyQt para geração de linhas digitáveis de boletos diretamente de títulos cadastrados no sistema interno WBA.

## Funcionalidades

- Busca dinâmica de pessoas (Cedentes e Sacados) por nome, CNPJ ou código
- Filtragem de títulos por empresa, bordero, data de bordero e data de vencimento
- Visualização de títulos em formato tabular
- Geração de linhas digitáveis para títulos selecionados de acordo com a empresa (SEC ou FIDC)
- Exportação de dados para Excel ou CSV
- Interface gráfica intuitiva e responsiva

## Requisitos

- Python 3.10+
- SQL Server (RDS na AWS)
- Driver ODBC para SQL Server

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/linha-digitavel-py.git
cd linha-digitavel-py
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env` com as informações de conexão ao banco de dados e as configurações do boleto:
```
# Configurações de conexão com o banco de dados
DB_SERVER=seu_servidor.amazonaws.com
DB_DATABASE=wba
DB_USERNAME=seu_usuario
DB_PASSWORD=sua_senha

# Configurações fixas para a linha digitável
BANCO=341
MOEDA=9
CARTEIRA=109
AGENCIA=1704

# Configurações específicas para FIDC
FIDC_CONTA=26957
FIDC_DAC_CONTA=8

# Configurações específicas para SEC
SEC_CONTA=17063
SEC_DAC_CONTA=6
```

## Execução

Execute o arquivo principal:
```bash
python main.py
```

## Uso

1. **Busca de Pessoas**:
   - Selecione o tipo (Cedente ou Sacado)
   - Digite o nome, CNPJ ou código para buscar
   - Selecione uma pessoa da lista de resultados

2. **Filtros de Títulos**:
   - Empresa: SEC, FIDC ou ambas
   - Bordero: número do bordero
   - Data do Bordero: período
   - Data de Vencimento: período
   - Clique em "Buscar Títulos"

3. **Ações com Títulos**:
   - Selecione um ou mais títulos da tabela
   - Clique em "Gerar Linha Digitável" para criar a linha digitável
   - Clique em "Copiar" para copiar a linha para a área de transferência
   - Clique em "Exportar para Excel" para exportar os dados para um arquivo Excel ou CSV

## Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação
- `db.py`: Módulo de conexão e consultas ao banco de dados
- `models.py`: Classes de modelo de dados (Pessoa, Titulo)
- `ui.py`: Interface gráfica com PyQt
- `linha_digitavel.py`: Funções para geração da linha digitável do boleto

## Observações

- Certifique-se de que o driver ODBC para SQL Server está instalado no sistema
- A aplicação requer acesso direto ao banco de dados SQL Server
- As configurações de boleto (carteira, agência, conta SEC, conta FIDC) devem ser configuradas no arquivo `.env`
- Para títulos do tipo SEC, serão usadas as configurações de SEC_CONTA e SEC_DAC_CONTA
- Para títulos do tipo FIDC, serão usadas as configurações de FIDC_CONTA e FIDC_DAC_CONTA 