import sys
import os
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QGroupBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QDateEdit, QMessageBox, QFileDialog, QCheckBox, QProgressBar,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate
from PyQt5.QtGui import QFont, QIcon

import pandas as pd
from dotenv import load_dotenv

from db import db_connection
from models import Pessoa, Titulo

# Carregar variáveis de ambiente
load_dotenv()

class BuscaThread(QThread):
    """Thread para realizar buscas assíncronas no banco de dados."""
    finished = pyqtSignal(list)
    
    def __init__(self, search_term, tipo):
        super().__init__()
        self.search_term = search_term
        self.tipo = tipo
        
    def run(self):
        resultados = db_connection.search_pessoas(self.search_term, self.tipo)
        self.finished.emit(resultados)

class TitulosThread(QThread):
    """Thread para buscar títulos assíncronos no banco de dados."""
    finished = pyqtSignal(list)
    
    def __init__(self, codigo_pessoa, tipo_pessoa, bordero=None,
                 data_bordero_inicial=None, data_bordero_final=None,
                 data_vencimento_inicial=None, data_vencimento_final=None,
                 empresa=None):
        super().__init__()
        self.codigo_pessoa = codigo_pessoa
        self.tipo_pessoa = tipo_pessoa
        self.bordero = bordero
        self.data_bordero_inicial = data_bordero_inicial
        self.data_bordero_final = data_bordero_final
        self.data_vencimento_inicial = data_vencimento_inicial
        self.data_vencimento_final = data_vencimento_final
        self.empresa = empresa
        
    def run(self):
        titulos = db_connection.get_titulos(
            codigo_pessoa=self.codigo_pessoa,
            tipo_pessoa=self.tipo_pessoa,
            bordero=self.bordero,
            data_bordero_inicial=self.data_bordero_inicial,
            data_bordero_final=self.data_bordero_final,
            data_vencimento_inicial=self.data_vencimento_inicial,
            data_vencimento_final=self.data_vencimento_final,
            empresa=self.empresa
        )
        self.finished.emit(titulos)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Linha Digitável - WBA")
        self.setMinimumSize(1200, 800)
        
        # Inicializar variáveis
        self.pessoa_selecionada = None
        self.titulos = []
        self.titulos_selecionados = []
        
        # Configurar a interface
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do usuário."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Seção de busca
        search_group = QGroupBox("Busca de Pessoa")
        search_layout = QVBoxLayout()
        
        # Layout para o tipo e termo de busca
        tipo_search_layout = QHBoxLayout()
        
        # Tipo de pessoa (Cedente ou Sacado)
        tipo_layout = QHBoxLayout()
        tipo_layout.addWidget(QLabel("Tipo:"))
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Cedente", "Sacado"])
        tipo_layout.addWidget(self.tipo_combo)
        tipo_search_layout.addLayout(tipo_layout)
        
        # Campo de busca
        search_layout_inner = QHBoxLayout()
        search_layout_inner.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite nome, CNPJ ou código...")
        search_layout_inner.addWidget(self.search_input)
        tipo_search_layout.addLayout(search_layout_inner)
        
        search_layout.addLayout(tipo_search_layout)
        
        # Lista de resultados
        search_layout.addWidget(QLabel("Resultados:"))
        self.results_list = QListWidget()
        search_layout.addWidget(self.results_list)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Seção de detalhes da pessoa
        self.person_details_group = QGroupBox("Detalhes da Pessoa")
        person_details_layout = QVBoxLayout()
        
        # Grid para exibir dados da pessoa
        person_data_layout = QHBoxLayout()
        
        self.person_nome_label = QLabel("Nome: ")
        person_data_layout.addWidget(self.person_nome_label)
        
        self.person_cgc_label = QLabel("CNPJ/CPF: ")
        person_data_layout.addWidget(self.person_cgc_label)
        
        self.person_codigo_label = QLabel("Código: ")
        person_data_layout.addWidget(self.person_codigo_label)
        
        self.person_tipo_label = QLabel("Tipo: ")
        person_data_layout.addWidget(self.person_tipo_label)
        
        person_details_layout.addLayout(person_data_layout)
        
        # Seção de filtros de títulos
        titulos_filter_layout = QHBoxLayout()
        
        # Filtro por empresa
        empresa_layout = QVBoxLayout()
        empresa_layout.addWidget(QLabel("Empresa:"))
        self.empresa_combo = QComboBox()
        self.empresa_combo.addItems(["Todas", "SEC", "FIDC"])
        empresa_layout.addWidget(self.empresa_combo)
        titulos_filter_layout.addLayout(empresa_layout)
        
        # Filtro por bordero
        bordero_layout = QVBoxLayout()
        bordero_layout.addWidget(QLabel("Bordero:"))
        self.bordero_input = QLineEdit()
        self.bordero_input.setPlaceholderText("Número do bordero")
        bordero_layout.addWidget(self.bordero_input)
        titulos_filter_layout.addLayout(bordero_layout)
        
        # Filtro por data do bordero
        data_bordero_layout = QVBoxLayout()
        data_bordero_layout.addWidget(QLabel("Data do Bordero:"))
        data_bordero_dates_layout = QHBoxLayout()
        
        self.data_bordero_inicial = QDateEdit(calendarPopup=True)
        self.data_bordero_inicial.setDate(QDate.currentDate().addDays(-30))
        data_bordero_dates_layout.addWidget(self.data_bordero_inicial)
        
        data_bordero_dates_layout.addWidget(QLabel("até"))
        
        self.data_bordero_final = QDateEdit(calendarPopup=True)
        self.data_bordero_final.setDate(QDate.currentDate())
        data_bordero_dates_layout.addWidget(self.data_bordero_final)
        
        data_bordero_layout.addLayout(data_bordero_dates_layout)
        titulos_filter_layout.addLayout(data_bordero_layout)
        
        # Filtro por data de vencimento
        data_vencimento_layout = QVBoxLayout()
        data_vencimento_layout.addWidget(QLabel("Data de Vencimento:"))
        data_vencimento_dates_layout = QHBoxLayout()
        
        self.data_vencimento_inicial = QDateEdit(calendarPopup=True)
        self.data_vencimento_inicial.setDate(QDate.currentDate())
        data_vencimento_dates_layout.addWidget(self.data_vencimento_inicial)
        
        data_vencimento_dates_layout.addWidget(QLabel("até"))
        
        self.data_vencimento_final = QDateEdit(calendarPopup=True)
        self.data_vencimento_final.setDate(QDate.currentDate().addDays(30))
        data_vencimento_dates_layout.addWidget(self.data_vencimento_final)
        
        data_vencimento_layout.addLayout(data_vencimento_dates_layout)
        titulos_filter_layout.addLayout(data_vencimento_layout)
        
        # Botão buscar títulos
        buscar_layout = QVBoxLayout()
        buscar_layout.addWidget(QLabel(""))  # Espaçador
        self.buscar_titulos_btn = QPushButton("Buscar Títulos")
        buscar_layout.addWidget(self.buscar_titulos_btn)
        titulos_filter_layout.addLayout(buscar_layout)
        
        person_details_layout.addLayout(titulos_filter_layout)
        
        self.person_details_group.setLayout(person_details_layout)
        self.person_details_group.setEnabled(False)
        main_layout.addWidget(self.person_details_group)
        
        # Tabela de títulos
        titulos_group = QGroupBox("Títulos")
        titulos_layout = QVBoxLayout()
        
        self.titulos_table = QTableWidget()
        self.titulos_table.setColumnCount(11)
        self.titulos_table.setHorizontalHeaderLabels([
            "Empresa", "Código", "Sacado", "Bordero", "Data Bordero", 
            "Núm. Documento", "Seu Número", "Cód. Documento", 
            "Tipo Documento", "Vencimento", "Valor"
        ])
        self.titulos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.titulos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.titulos_table.setSelectionMode(QTableWidget.MultiSelection)
        titulos_layout.addWidget(self.titulos_table)
        
        # Layout para botões de ação
        buttons_layout = QHBoxLayout()
        
        self.gerar_linha_btn = QPushButton("Gerar Linha Digitável")
        self.gerar_linha_btn.setEnabled(False)
        buttons_layout.addWidget(self.gerar_linha_btn)
        
        self.exportar_btn = QPushButton("Exportar para Excel")
        self.exportar_btn.setEnabled(False)
        buttons_layout.addWidget(self.exportar_btn)
        
        titulos_layout.addLayout(buttons_layout)
        
        # Linhas digitáveis geradas
        titulos_layout.addWidget(QLabel("Linhas Digitáveis Geradas:"))
        self.linhas_text = QLineEdit()
        self.linhas_text.setReadOnly(True)
        self.linhas_text.setPlaceholderText("Selecione títulos e clique em 'Gerar Linha Digitável'")
        titulos_layout.addWidget(self.linhas_text)
        
        # Botão para copiar
        self.copiar_btn = QPushButton("Copiar")
        self.copiar_btn.setEnabled(False)
        titulos_layout.addWidget(self.copiar_btn)
        
        titulos_group.setLayout(titulos_layout)
        main_layout.addWidget(titulos_group)
        
        # Seção de configurações do boleto
        config_group = QGroupBox("Configurações do Boleto")
        config_layout = QHBoxLayout()
        
        self.banco_label = QLabel(f"Banco: {os.getenv('BANCO')}")
        config_layout.addWidget(self.banco_label)
        
        self.moeda_label = QLabel(f"Moeda: {os.getenv('MOEDA')}")
        config_layout.addWidget(self.moeda_label)
        
        self.carteira_label = QLabel(f"Carteira: {os.getenv('CARTEIRA')}")
        config_layout.addWidget(self.carteira_label)
        
        self.agencia_label = QLabel(f"Agência: {os.getenv('AGENCIA')}")
        config_layout.addWidget(self.agencia_label)
        
        self.conta_label = QLabel(f"Conta FIDC: {os.getenv('FIDC_CONTA')}")
        config_layout.addWidget(self.conta_label)
        
        self.dac_conta_label = QLabel(f"DAC Conta FIDC: {os.getenv('FIDC_DAC_CONTA')}")
        config_layout.addWidget(self.dac_conta_label)
        
        self.conta_label = QLabel(f"Conta SEC: {os.getenv('SEC_CONTA')}")
        config_layout.addWidget(self.conta_label)
        
        self.dac_conta_label = QLabel(f"DAC Conta SEC: {os.getenv('SEC_DAC_CONTA')}")
        config_layout.addWidget(self.dac_conta_label)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # Conectar eventos
        self.connect_events()
    
    def connect_events(self):
        """Conecta os eventos da interface com suas funções."""
        # Timer para busca dinâmica
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        # Busca dinâmica ao digitar
        self.search_input.textChanged.connect(self.start_search_timer)
        
        # Seleção de pessoa na lista
        self.results_list.itemClicked.connect(self.select_pessoa)
        
        # Buscar títulos
        self.buscar_titulos_btn.clicked.connect(self.buscar_titulos)
        
        # Seleção de títulos na tabela
        self.titulos_table.itemSelectionChanged.connect(self.update_buttons_state)
        
        # Gerar linha digitável
        self.gerar_linha_btn.clicked.connect(self.gerar_linhas_digitaveis)
        
        # Exportar para Excel
        self.exportar_btn.clicked.connect(self.exportar_para_excel)
        
        # Copiar linha digitável
        self.copiar_btn.clicked.connect(self.copiar_linha)
    
    def start_search_timer(self):
        """Inicia o timer para busca dinâmica."""
        self.search_timer.start(300)  # 300 ms de atraso para evitar sobrecarga
    
    def perform_search(self):
        """Realiza a busca de pessoas no banco de dados."""
        search_term = self.search_input.text().strip()
        if len(search_term) < 2:
            self.results_list.clear()
            return
        
        tipo = self.tipo_combo.currentText()
        
        # Usar thread para não bloquear a interface
        self.search_thread = BuscaThread(search_term, tipo)
        self.search_thread.finished.connect(self.update_search_results)
        self.search_thread.start()
    
    def update_search_results(self, results):
        """Atualiza a lista de resultados com os dados encontrados."""
        self.results_list.clear()
        
        for pessoa in results:
            display_text = f"{pessoa['nome']} - CNPJ: {pessoa['cgc']} - Código: {pessoa['codigo']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, pessoa)
            self.results_list.addItem(item)
    
    def select_pessoa(self, item):
        """Seleciona uma pessoa da lista e ativa os filtros de títulos."""
        pessoa_data = item.data(Qt.UserRole)
        self.pessoa_selecionada = Pessoa.from_dict(pessoa_data)
        
        # Atualizar labels com dados da pessoa
        self.person_nome_label.setText(f"Nome: {self.pessoa_selecionada.nome}")
        self.person_cgc_label.setText(f"CNPJ/CPF: {self.pessoa_selecionada.cgc}")
        self.person_codigo_label.setText(f"Código: {self.pessoa_selecionada.codigo}")
        self.person_tipo_label.setText(f"Tipo: {self.pessoa_selecionada.tipo}")
        
        # Ativar seção de filtros
        self.person_details_group.setEnabled(True)
        
        # Limpar títulos anteriores
        self.titulos_table.setRowCount(0)
        self.titulos = []
        self.update_buttons_state()
    
    def buscar_titulos(self):
        """Busca títulos no banco de dados com os filtros especificados."""
        if not self.pessoa_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma pessoa primeiro.")
            return
        
        # Capturar valores dos filtros
        empresa = self.empresa_combo.currentText()
        if empresa == "Todas":
            empresa = None
        
        bordero = self.bordero_input.text().strip()
        if bordero and bordero.isdigit():
            bordero = int(bordero)
        else:
            bordero = None
        
        data_bordero_inicial = self.data_bordero_inicial.date().toString("yyyy-MM-dd")
        data_bordero_final = self.data_bordero_final.date().toString("yyyy-MM-dd")
        
        data_vencimento_inicial = self.data_vencimento_inicial.date().toString("yyyy-MM-dd")
        data_vencimento_final = self.data_vencimento_final.date().toString("yyyy-MM-dd")
        
        # Usar thread para não bloquear a interface
        self.titulos_thread = TitulosThread(
            codigo_pessoa=self.pessoa_selecionada.codigo,
            tipo_pessoa=self.pessoa_selecionada.tipo,
            bordero=bordero,
            data_bordero_inicial=data_bordero_inicial,
            data_bordero_final=data_bordero_final,
            data_vencimento_inicial=data_vencimento_inicial,
            data_vencimento_final=data_vencimento_final,
            empresa=empresa
        )
        self.titulos_thread.finished.connect(self.exibir_titulos)
        self.titulos_thread.start()
    
    def exibir_titulos(self, titulos_data):
        """Exibe os títulos encontrados na tabela."""
        self.titulos_table.setRowCount(0)
        self.titulos = []
        
        if not titulos_data:
            QMessageBox.information(self, "Informação", "Nenhum título encontrado com os filtros especificados.")
            return
        
        # Converter dados para objetos Titulo
        for titulo_data in titulos_data:
            titulo = Titulo.from_dict(titulo_data)
            self.titulos.append(titulo)
        
        # Preencher a tabela
        self.titulos_table.setRowCount(len(self.titulos))
        
        for row, titulo in enumerate(self.titulos):
            data_bordero_str = titulo.data_bordero.strftime("%d/%m/%Y")
            vencimento_str = titulo.vencimento.strftime("%d/%m/%Y")
            valor_str = f"{titulo.valor:.2f}".replace('.', ',')
            
            self.titulos_table.setItem(row, 0, QTableWidgetItem(titulo.empresa))
            self.titulos_table.setItem(row, 1, QTableWidgetItem(str(titulo.codigo)))
            self.titulos_table.setItem(row, 2, QTableWidgetItem(str(titulo.sacado)))
            self.titulos_table.setItem(row, 3, QTableWidgetItem(str(titulo.bordero)))
            self.titulos_table.setItem(row, 4, QTableWidgetItem(data_bordero_str))
            self.titulos_table.setItem(row, 5, QTableWidgetItem(titulo.numero_documento))
            self.titulos_table.setItem(row, 6, QTableWidgetItem(titulo.seu_numero))
            self.titulos_table.setItem(row, 7, QTableWidgetItem(titulo.codigo_dcto))
            self.titulos_table.setItem(row, 8, QTableWidgetItem(titulo.tipodcto))
            self.titulos_table.setItem(row, 9, QTableWidgetItem(vencimento_str))
            self.titulos_table.setItem(row, 10, QTableWidgetItem(valor_str))
        
        self.exportar_btn.setEnabled(True)
        self.update_buttons_state()
    
    def update_buttons_state(self):
        """Atualiza o estado dos botões com base na seleção de títulos."""
        selected_rows = len(self.titulos_table.selectedItems()) // self.titulos_table.columnCount()
        self.gerar_linha_btn.setEnabled(selected_rows > 0)
        self.copiar_btn.setEnabled(self.linhas_text.text() != "")
    
    def gerar_linhas_digitaveis(self):
        """Gera as linhas digitáveis para os títulos selecionados."""
        selected_rows = set()
        
        for item in self.titulos_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um título.")
            return
        
        linhas = []
        self.titulos_selecionados = []
        
        for row in selected_rows:
            titulo = self.titulos[row]
            linha = titulo.gerar_linha_digitavel()
            linhas.append(linha)
            self.titulos_selecionados.append(titulo)
        
        # Exibir linhas geradas
        self.linhas_text.setText(" | ".join(linhas))
        self.copiar_btn.setEnabled(True)
    
    def copiar_linha(self):
        """Copia a linha digitável para a área de transferência."""
        QApplication.clipboard().setText(self.linhas_text.text())
        QMessageBox.information(self, "Sucesso", "Texto copiado para a área de transferência.")
    
    def exportar_para_excel(self):
        """Exporta os títulos selecionados para um arquivo Excel ou CSV."""
        if not self.titulos:
            QMessageBox.warning(self, "Aviso", "Não há títulos para exportar.")
            return
        
        # Perguntar se quer exportar todos ou apenas os selecionados
        dialog = QMessageBox()
        dialog.setWindowTitle("Exportar Títulos")
        dialog.setText("Deseja exportar todos os títulos ou apenas os selecionados?")
        todos_btn = dialog.addButton("Todos", QMessageBox.YesRole)
        selecionados_btn = dialog.addButton("Selecionados", QMessageBox.NoRole)
        cancelar_btn = dialog.addButton("Cancelar", QMessageBox.RejectRole)
        
        dialog.exec_()
        
        if dialog.clickedButton() == cancelar_btn:
            return
        
        # Determinar quais títulos exportar
        if dialog.clickedButton() == todos_btn:
            titulos_exportar = self.titulos
        else:  # Selecionados
            selected_rows = set()
            for item in self.titulos_table.selectedItems():
                selected_rows.add(item.row())
            
            if not selected_rows:
                QMessageBox.warning(self, "Aviso", "Selecione pelo menos um título para exportar.")
                return
            
            titulos_exportar = [self.titulos[row] for row in selected_rows]
        
        # Perguntar formato
        format_dialog = QMessageBox()
        format_dialog.setWindowTitle("Formato de Exportação")
        format_dialog.setText("Escolha o formato do arquivo:")
        xlsx_btn = format_dialog.addButton("Excel (XLSX)", QMessageBox.YesRole)
        csv_btn = format_dialog.addButton("CSV", QMessageBox.NoRole)
        cancel_format_btn = format_dialog.addButton("Cancelar", QMessageBox.RejectRole)
        
        format_dialog.exec_()
        
        if format_dialog.clickedButton() == cancel_format_btn:
            return
        
        # Determinar formato de arquivo
        extension = "xlsx" if format_dialog.clickedButton() == xlsx_btn else "csv"
        
        # Gerar linhas digitáveis para os títulos selecionados
        for titulo in titulos_exportar:
            if not titulo.linha_digitavel:
                titulo.gerar_linha_digitavel()
        
        # Preparar dados para exportação
        dados = []
        for titulo in titulos_exportar:
            dados.append({
                'empresa': titulo.empresa,
                'cedente': titulo.codigo,
                'sacado': titulo.sacado,
                'bordero': titulo.bordero,
                'data_bordero': titulo.data_bordero.strftime('%d/%m/%Y'),
                'numero_documento': titulo.numero_documento,
                'seu_numero': titulo.seu_numero,
                'tipodcto': titulo.tipodcto,
                'vencimento': titulo.vencimento.strftime('%d/%m/%Y'),
                'valor': titulo.valor,
                'linha_digitavel': titulo.linha_digitavel
            })
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Definir local para salvar o arquivo
        default_file = f"titulos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Arquivo", 
            default_file, 
            f"{'Excel' if extension == 'xlsx' else 'CSV'} Files (*.{extension})"
        )
        
        if not file_path:
            return
        
        try:
            # Exportar dados
            if extension == 'xlsx':
                df.to_excel(file_path, index=False, engine='openpyxl')
            else:
                df.to_csv(file_path, index=False, sep=';', encoding='utf-8')
            
            QMessageBox.information(self, "Sucesso", f"Arquivo exportado com sucesso para:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar arquivo:\n{str(e)}")
            
    def closeEvent(self, event):
        """Fecha a conexão com o banco de dados ao fechar a aplicação."""
        db_connection.disconnect()
        event.accept() 