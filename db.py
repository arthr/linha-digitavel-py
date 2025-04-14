import os
import pyodbc
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        
    def connect(self) -> bool:
        """Estabelece conexão com o banco de dados."""
        try:
            connection_string = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password}'
            )
            self.connection = pyodbc.connect(connection_string)
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            return False
    
    def disconnect(self) -> None:
        """Fecha a conexão com o banco de dados se estiver aberta."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except Exception as e:
                logger.error(f"Erro ao fechar conexão com o banco de dados: {e}")
    
    def execute_query(self, query: str, params: Tuple = None) -> Optional[List[Dict[str, Any]]]:
        """Executa uma consulta SQL e retorna os resultados como uma lista de dicionários."""
        if not self.connection and not self.connect():
            return None
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Extrair nomes das colunas
            columns = [column[0] for column in cursor.description]
            
            # Converter resultados para lista de dicionários
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parâmetros: {params}")
            return None
    
    def execute_non_query(self, query: str, params: Tuple = None) -> bool:
        """Executa uma instrução SQL (INSERT, UPDATE, DELETE) sem retorno de dados."""
        if not self.connection and not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao executar instrução: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parâmetros: {params}")
            return False

    def search_pessoas(self, search_term: str, tipo: str) -> List[Dict[str, Any]]:
        """Busca pessoas por nome, CGC ou código com o tipo especificado."""
        query = """
        SELECT TOP(15) id, codigo, nome, cgc, tipo
        FROM sigcad
        WHERE tipo = ?
        AND (nome LIKE ? OR cgc LIKE ? OR codigo = ?)
        ORDER BY nome
        """
        
        try:
            # Verifica se o termo de busca é um número (para código)
            if search_term.isdigit():
                codigo = int(search_term)
            else:
                codigo = -1  # Valor inválido para garantir que não encontre por código
                
            params = (tipo, f'%{search_term}%', f'%{search_term}%', codigo)
            return self.execute_query(query, params) or []
        except Exception as e:
            logger.error(f"Erro na busca de pessoas: {e}")
            return []
            
    def get_titulos(self, 
                    codigo_pessoa: int = None,
                    tipo_pessoa: str = None,
                    bordero: int = None,
                    data_bordero_inicial: str = None, 
                    data_bordero_final: str = None,
                    data_vencimento_inicial: str = None, 
                    data_vencimento_final: str = None,
                    empresa: str = None) -> List[Dict[str, Any]]:
        """
        Busca títulos com os filtros especificados.
        
        Args:
            codigo_pessoa: Código da pessoa (Cedente ou Sacado)
            tipo_pessoa: Tipo da pessoa ("Cedente" ou "Sacado")
            bordero: Número do bordero (opcional)
            data_bordero_inicial: Data inicial do bordero (opcional)
            data_bordero_final: Data final do bordero (opcional)
            data_vencimento_inicial: Data inicial de vencimento (opcional)
            data_vencimento_final: Data final de vencimento (opcional)
            empresa: Empresa (SEC ou FIDC) (opcional)
            
        Returns:
            Lista de títulos encontrados
        """
        # Base da consulta
        query_fidc = """
        SELECT
        f.id,
        'FIDC' AS empresa,
        f.clifor AS codigo,
        f.sacado,
        f.bordero,
        CAST(f.dtbordero AS DATE) AS data_bordero,
        f.dcto AS numero_documento,
        fidc.numero_port AS seu_numero,
        f.codigo AS codigo_dcto,
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
        """
        
        query_sec = """
        SELECT
        f.id,
        'SEC' AS empresa,
        f.clifor AS codigo,
        f.sacado,
        f.bordero,
        CAST(f.dtbordero AS DATE) AS data_bordero,
        f.dcto AS numero_documento,
        sec.numero_port AS seu_numero,
        f.codigo AS codigo_dcto,
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
        """
        
        # Parâmetros base
        params_fidc = []
        params_sec = []
        
        # Adiciona filtro de pessoa (Cedente ou Sacado) se fornecido
        if codigo_pessoa and tipo_pessoa:
            if tipo_pessoa == "Cedente":
                query_fidc += " AND f.clifor = ?"
                query_sec += " AND f.clifor = ?"
                params_fidc.append(codigo_pessoa)
                params_sec.append(codigo_pessoa)
            elif tipo_pessoa == "Sacado":
                query_fidc += " AND f.sacado = ?"
                query_sec += " AND f.sacado = ?"
                params_fidc.append(codigo_pessoa)
                params_sec.append(codigo_pessoa)
        
        # Adiciona filtro de bordero se fornecido
        if bordero:
            query_fidc += " AND f.bordero = ?"
            query_sec += " AND f.bordero = ?"
            params_fidc.append(bordero)
            params_sec.append(bordero)
        
        # Adiciona filtro de data do bordero se fornecido
        if data_bordero_inicial and data_bordero_final:
            query_fidc += " AND CAST(f.dtbordero AS DATE) BETWEEN ? AND ?"
            query_sec += " AND CAST(f.dtbordero AS DATE) BETWEEN ? AND ?"
            params_fidc.extend([data_bordero_inicial, data_bordero_final])
            params_sec.extend([data_bordero_inicial, data_bordero_final])
        
        # Adiciona filtro de data de vencimento se fornecido
        if data_vencimento_inicial and data_vencimento_final:
            query_fidc += " AND CAST(fidc.vcto_ AS DATE) BETWEEN ? AND ?"
            query_sec += " AND CAST(sec.vcto_ AS DATE) BETWEEN ? AND ?"
            params_fidc.extend([data_vencimento_inicial, data_vencimento_final])
            params_sec.extend([data_vencimento_inicial, data_vencimento_final])
        
        # Executa a consulta com base no filtro de empresa
        if empresa == "FIDC":
            return self.execute_query(query_fidc, tuple(params_fidc)) or []
        elif empresa == "SEC":
            return self.execute_query(query_sec, tuple(params_sec)) or []
        else:
            # Se não houver filtro de empresa, executa ambas as consultas e une os resultados
            query = f"{query_fidc} UNION ALL {query_sec}"
            params = params_fidc + params_sec
            return self.execute_query(query, tuple(params)) or []

# Instância global para uso em todo o projeto
db_connection = DatabaseConnection() 