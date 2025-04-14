from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import logging

# Importação da função de geração de linha digitável
from linha_digitavel import gerar_linha_digitavel

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

@dataclass
class Pessoa:
    """Classe que representa uma pessoa (Cedente ou Sacado) no sistema."""
    id: int
    codigo: int
    nome: str
    cgc: str
    tipo: str  # "Cedente" ou "Sacado"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pessoa':
        """Cria uma instância de Pessoa a partir de um dicionário."""
        return cls(
            id=data['id'],
            codigo=data['codigo'],
            nome=data['nome'],
            cgc=data['cgc'],
            tipo=data['tipo']
        )

@dataclass
class Titulo:
    """Classe que representa um título no sistema."""
    id: int
    empresa: str  # "SEC" ou "FIDC"
    codigo: int
    sacado: int
    bordero: int
    data_bordero: date
    numero_documento: str
    seu_numero: str
    codigo_dcto: str
    tipodcto: str
    vencimento: date
    valor: float
    linha_digitavel: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Titulo':
        """Cria uma instância de Titulo a partir de um dicionário."""
        # Converter strings de data para objetos date
        try:
            data_bordero = data['data_bordero']
            if isinstance(data_bordero, str):
                data_bordero = datetime.strptime(data_bordero, '%Y-%m-%d').date()
            
            vencimento = data['vencimento']
            if isinstance(vencimento, str):
                vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
            
            return cls(
                id=data['id'],
                empresa=data['empresa'],
                codigo=data['codigo'],
                sacado=data['sacado'],
                bordero=data['bordero'],
                data_bordero=data_bordero,
                numero_documento=data['numero_documento'],
                seu_numero=data['seu_numero'],
                codigo_dcto=data['codigo_dcto'],
                tipodcto=data['tipodcto'],
                vencimento=vencimento,
                valor=float(data['valor'])
            )
        except Exception as e:
            logger.error(f"Erro ao criar Titulo: {e}")
            logger.error(f"Dados: {data}")
            raise
    
    def gerar_linha_digitavel(self) -> str:
        """Gera a linha digitável para o título usando os dados fixos do .env"""
        try:
            # Obter dados do ambiente
            carteira = os.getenv('CARTEIRA')
            agencia = os.getenv('AGENCIA')
            
            if self.empresa == 'FIDC':
                conta = os.getenv('FIDC_CONTA')
                dac_conta = os.getenv('FIDC_DAC_CONTA')
            else:
                conta = os.getenv('SEC_CONTA')
                dac_conta = os.getenv('SEC_DAC_CONTA')
            
            # Extrai o número e DAC do nosso número do seu_numero
            # Assumindo que seu_numero contém o nosso número (8 dígitos) seguido do DAC (1 dígito)
            nosso_numero = self.seu_numero[:8]
            dac_nosso_numero = self.seu_numero[8:9]
            
            # Formatar data de vencimento como string dd/mm/yyyy
            vencimento_str = self.vencimento.strftime('%d/%m/%Y')
            
            # Gerar linha digitável
            self.linha_digitavel = gerar_linha_digitavel(
                vencimento=vencimento_str,
                valor=str(self.valor),
                carteira=carteira,
                nosso_numero=nosso_numero,
                agencia=agencia,
                conta=conta,
                dac_nosso_numero=dac_nosso_numero,
                dac_conta=dac_conta
            )
            
            return self.linha_digitavel
        except Exception as e:
            logger.error(f"Erro ao gerar linha digitável: {e}")
            return "Erro na geração da linha digitável"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o título para um dicionário, incluindo a linha digitável."""
        if not self.linha_digitavel:
            self.gerar_linha_digitavel()
            
        return {
            'id': self.id,
            'empresa': self.empresa,
            'codigo': self.codigo,
            'sacado': self.sacado,
            'bordero': self.bordero,
            'data_bordero': self.data_bordero.strftime('%d/%m/%Y'),
            'numero_documento': self.numero_documento,
            'seu_numero': self.seu_numero,
            'codigo_dcto': self.codigo_dcto,
            'tipodcto': self.tipodcto,
            'vencimento': self.vencimento.strftime('%d/%m/%Y'),
            'valor': self.valor,
            'linha_digitavel': self.linha_digitavel
        } 