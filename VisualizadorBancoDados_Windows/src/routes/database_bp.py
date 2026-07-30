import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

@contextmanager
def get_db_connection():
    """Context manager para conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela para Cálculos VNA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculos_vna (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vne REAL NOT NULL,
                ipca_emissao REAL NOT NULL,
                ipca_atual REAL NOT NULL,
                vna_calculado REAL NOT NULL,
                fator_correcao REAL NOT NULL,
                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Ativo'
            )
        ''')
        
        # Tabela para PU PAR
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pu_par (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vna REAL NOT NULL,
                taxa_juros REAL NOT NULL,
                dias_uteis INTEGER NOT NULL,
                base_calculo INTEGER NOT NULL,
                pu_par REAL NOT NULL,
                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Ativo'
            )
        ''')
        
        # Tabela para PU Operação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pu_operacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_if TEXT,
                nome_ativo TEXT,
                taxa_mercado REAL NOT NULL,
                base_calculo INTEGER NOT NULL,
                pu_operacao REAL NOT NULL,
                indexador TEXT,
                emissor TEXT,
                data_vencimento TEXT,
                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Ativo'
            )
        ''')
        
        # Tabela para Filtros Estatísticos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filtros_estatisticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_filtro TEXT NOT NULL,
                parametros TEXT NOT NULL,
                resultados TEXT NOT NULL,
                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Ativo'
            )
        ''')
        
        # Tabela para Ativos Cadastrados (baseado na imagem)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_if TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                emissor TEXT NOT NULL,
                pu_emissao REAL,
                taxa REAL,
                indexador TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Ativo'
            )
        ''')
        
        # Tabela para Cálculos de Juros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculos_juros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_if TEXT NOT NULL,
                data_calculo_dia25 TEXT NOT NULL,
                vna REAL NOT NULL,
                porcentagem REAL NOT NULL,
                juros_calculado REAL NOT NULL,
                data_insercao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Ativo'
            )
        ''')
        
        # Tabela de Logs (para auditoria)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_operacao TEXT NOT NULL,
                tabela TEXT NOT NULL,
                registro_id INTEGER,
                detalhes TEXT,
                data_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("[OK] Banco de dados inicializado com sucesso!")

# Funções CRUD para Cálculos VNA
def salvar_calculo_vna(vne, ipca_emissao, ipca_atual, vna_calculado, fator_correcao):
    """Salva um cálculo VNA no banco de dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO calculos_vna (vne, ipca_emissao, ipca_atual, vna_calculado, fator_correcao)
            VALUES (?, ?, ?, ?, ?)
        ''', (vne, ipca_emissao, ipca_atual, vna_calculado, fator_correcao))
        return cursor.lastrowid

def listar_calculos_vna():
    """Lista todos os cálculos VNA"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calculos_vna ORDER BY data_calculo DESC')
        return [dict(row) for row in cursor.fetchall()]

def atualizar_calculo_vna(id, dados):
    """Atualiza um cálculo VNA existente"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        campos = ', '.join([f"{k} = ?" for k in dados.keys()])
        valores = list(dados.values()) + [id]
        cursor.execute(f'UPDATE calculos_vna SET {campos} WHERE id = ?', valores)
        return cursor.rowcount > 0

def deletar_calculo_vna(id):
    """Deleta (marca como inativo) um cálculo VNA"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE calculos_vna SET status = ? WHERE id = ?', ('Inativo', id))
        return cursor.rowcount > 0

# Funções CRUD para PU PAR
def salvar_pu_par(vna, taxa_juros, dias_uteis, base_calculo, pu_par):
    """Salva um cálculo PU PAR no banco de dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pu_par (vna, taxa_juros, dias_uteis, base_calculo, pu_par)
            VALUES (?, ?, ?, ?, ?)
        ''', (vna, taxa_juros, dias_uteis, base_calculo, pu_par))
        return cursor.lastrowid

def listar_pu_par():
    """Lista todos os cálculos PU PAR"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pu_par ORDER BY data_calculo DESC')
        return [dict(row) for row in cursor.fetchall()]

# Funções CRUD para PU Operação
def salvar_pu_operacao(codigo_if, nome_ativo, taxa_mercado, base_calculo, pu_operacao, 
                       indexador=None, emissor=None, data_vencimento=None):
    """Salva um cálculo PU Operação no banco de dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pu_operacao (codigo_if, nome_ativo, taxa_mercado, base_calculo, 
                                     pu_operacao, indexador, emissor, data_vencimento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (codigo_if, nome_ativo, taxa_mercado, base_calculo, pu_operacao, 
              indexador, emissor, data_vencimento))
        return cursor.lastrowid

def listar_pu_operacao():
    """Lista todos os cálculos PU Operação"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pu_operacao ORDER BY data_calculo DESC')
        return [dict(row) for row in cursor.fetchall()]

# Funções CRUD para Ativos
def salvar_ativo(codigo_if, nome, emissor, pu_emissao=None, taxa=None, indexador=None):
    """Salva um ativo no banco de dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO ativos (codigo_if, nome, emissor, pu_emissao, taxa, indexador)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (codigo_if, nome, emissor, pu_emissao, taxa, indexador))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Se o código IF já existe, atualiza
            cursor.execute('''
                UPDATE ativos 
                SET nome = ?, emissor = ?, pu_emissao = ?, taxa = ?, indexador = ?
                WHERE codigo_if = ?
            ''', (nome, emissor, pu_emissao, taxa, indexador, codigo_if))
            return None

def listar_ativos():
    """Lista todos os ativos cadastrados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ativos WHERE status = ? ORDER BY data_cadastro DESC', ('Ativo',))
        return [dict(row) for row in cursor.fetchall()]

def buscar_ativo_por_codigo(codigo_if):
    """Busca um ativo pelo código IF"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ativos WHERE codigo_if = ? AND status = ?', (codigo_if, 'Ativo'))
        row = cursor.fetchone()
        return dict(row) if row else None

def atualizar_ativo(id, dados):
    """Atualiza um ativo existente"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        campos = ', '.join([f"{k} = ?" for k in dados.keys()])
        valores = list(dados.values()) + [id]
        cursor.execute(f'UPDATE ativos SET {campos} WHERE id = ?', valores)
        return cursor.rowcount > 0

def deletar_ativo(id):
    """Deleta (marca como inativo) um ativo"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE ativos SET status = ? WHERE id = ?', ('Inativo', id))
        return cursor.rowcount > 0

# Funções para estatísticas
def contar_registros():
    """Retorna contagem de registros em cada tabela"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM calculos_vna WHERE status = ?', ('Ativo',))
        stats['calculos_vna'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM pu_par WHERE status = ?', ('Ativo',))
        stats['pu_par'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM pu_operacao WHERE status = ?', ('Ativo',))
        stats['pu_operacao'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM ativos WHERE status = ?', ('Ativo',))
        stats['ativos'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM filtros_estatisticos WHERE status = ?', ('Ativo',))
        stats['filtros'] = cursor.fetchone()[0]
        
        return stats

# Registrar log de operações
def registrar_log(tipo_operacao, tabela, registro_id=None, detalhes=None):
    """Registra uma operação no log"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (tipo_operacao, tabela, registro_id, detalhes)
            VALUES (?, ?, ?, ?)
        ''', (tipo_operacao, tabela, registro_id, detalhes))

def listar_logs(limite=100):
    """Lista os últimos logs"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY data_log DESC LIMIT ?', (limite,))
        return [dict(row) for row in cursor.fetchall()]


# Funções CRUD para Cálculos de Juros
def salvar_calculo_juros(codigo_if, data_calculo_dia25, vna, porcentagem, juros_calculado):
    """Salva um cálculo de juros no banco de dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO calculos_juros (codigo_if, data_calculo_dia25, vna, porcentagem, juros_calculado)
            VALUES (?, ?, ?, ?, ?)
        ''', (codigo_if, data_calculo_dia25, vna, porcentagem, juros_calculado))
        return cursor.lastrowid

def listar_calculos_juros():
    """Lista todos os cálculos de juros"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calculos_juros WHERE status = ? ORDER BY data_insercao DESC', ('Ativo',))
        return [dict(row) for row in cursor.fetchall()]

def obter_historico_juros(codigo_if=None, limite=100):
    """Obtém histórico de cálculos de juros"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if codigo_if:
            cursor.execute('''
                SELECT * FROM calculos_juros 
                WHERE codigo_if = ? AND status = ? 
                ORDER BY data_insercao DESC 
                LIMIT ?
            ''', (codigo_if, 'Ativo', limite))
        else:
            cursor.execute('''
                SELECT * FROM calculos_juros 
                WHERE status = ? 
                ORDER BY data_insercao DESC 
                LIMIT ?
            ''', ('Ativo', limite))
        
        return [dict(row) for row in cursor.fetchall()]

def buscar_calculo_juros_por_data(codigo_if, data_calculo_dia25):
    """Busca um cálculo de juros específico"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM calculos_juros 
            WHERE codigo_if = ? AND data_calculo_dia25 = ? AND status = ?
        ''', (codigo_if, data_calculo_dia25, 'Ativo'))
        row = cursor.fetchone()
        return dict(row) if row else None

def atualizar_calculo_juros(id, dados):
    """Atualiza um cálculo de juros existente"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        campos = ', '.join([f"{k} = ?" for k in dados.keys()])
        valores = list(dados.values()) + [id]
        cursor.execute(f'UPDATE calculos_juros SET {campos} WHERE id = ?', valores)
        return cursor.rowcount > 0

def deletar_calculo_juros(id):
    """Deleta (marca como inativo) um cálculo de juros"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE calculos_juros SET status = ? WHERE id = ?', ('Inativo', id))
        return cursor.rowcount > 0