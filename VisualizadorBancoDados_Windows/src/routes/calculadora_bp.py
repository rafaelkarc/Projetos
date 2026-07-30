from datetime import datetime
import sys
import os
import json
from flask import Blueprint, request, jsonify

import requests

def buscar_ipca_atual():
    """
    Busca o IPCA mais recente diretamente da API do IBGE (SIDRA)
    """
    try:
        url = "https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/63/p/last%201/d/v63%201"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        valor = float(data[1]['V'])  # Valor do IPCA
        print(f"✅ IPCA atual obtido do IBGE: {valor}")
        return valor
    except Exception as e:
        print(f"⚠️ Erro ao buscar IPCA no IBGE: {e}")
        return None


# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Supondo que excel_generator.py e asset_identifier.py existam e estejam corretos
try:
    from src.database import (
        init_database,
        salvar_calculo_vna,
        salvar_pu_par,
        salvar_pu_operacao,
        salvar_ativo
    )
    DATABASE_ENABLED = True
    print("✅ Módulo database importado com sucesso!")
except Exception as e:
    DATABASE_ENABLED = False
    print(f"⚠️ Erro ao importar database: {e}")
    # Criar funções dummy para não quebrar o sistema
    def salvar_calculo_vna(*args, **kwargs): pass
    def salvar_pu_par(*args, **kwargs): pass
    def salvar_pu_operacao(*args, **kwargs): pass
    def salvar_ativo(*args, **kwargs): pass

from src.excel_generator import (
    save_calculation_to_spreadsheet,
    save_pu_par_to_spreadsheet,
    save_pu_operacao_to_spreadsheet,
    save_filtros_estatisticos_to_spreadsheet,
    calcular_pu_par,
    calcular_pu_operacao,
    aplicar_filtros_estatisticos
)
from src.asset_identifier import AssetIdentifier
from src.juros_calculator import JurosCalculator


calculadora_bp = Blueprint("calculadora", __name__)


# Caminho do arquivo da planilha (corrigido para apontar para o diretório raiz)
PLANILHA_PU_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "planilha_pu.xlsx")


# FUNÇÃO PARA ENCONTRAR A PLANILHA AUTOMATICAMENTE (VERSÃO CORRIGIDA)
def encontrar_planilha():
    """
    Encontra automaticamente a planilha de operações em diferentes localizações possíveis
    """
    nomes_possiveis = [
        "operacoes.xlsx",
        "CaracterísticasdeCRI-LOGOS-v4-Operacoes.xlsx",
        "Características de CRI - LOGOS - v4 - Operacoes.xlsx",
        "Caracteristicas de CRI - LOGOS - v4 - Operacoes.xlsx"
    ]
    
    # Diretório atual onde o Flask está executando
    diretorio_atual = os.getcwd()
    print(f"🔍 Procurando planilha a partir de: {diretorio_atual}")
    
    # Diretório raiz do sistema (onde estão as planilhas)
    diretorio_raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    diretorios_possiveis = [
        diretorio_atual,  # Diretório atual
        diretorio_raiz,   # Diretório raiz do sistema
        os.path.join(diretorio_atual, "sistema_corrigido"),  # Subdiretório sistema_corrigido
        os.path.dirname(diretorio_atual),  # Diretório pai
        os.path.dirname(__file__),  # Diretório do arquivo atual
        os.path.dirname(os.path.dirname(__file__)),  # Dois níveis acima
    ]
    
    # Adicionar diretórios específicos do Windows se existirem
    if os.name == 'nt':  # Windows
        desktop_paths = [
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]
        diretorios_possiveis.extend(desktop_paths)
    
    for diretorio in diretorios_possiveis:
        if not os.path.exists(diretorio):
            continue
            
        print(f"🔍 Verificando diretório: {diretorio}")
        
        for nome in nomes_possiveis:
            caminho = os.path.join(diretorio, nome)
            if os.path.exists(caminho):
                print(f"✅ Planilha encontrada: {caminho}")
                return caminho
    
    # Busca recursiva no diretório atual (limitada a 2 níveis)
    print("🔍 Fazendo busca recursiva...")
    for root, dirs, files in os.walk(diretorio_atual):
        # Limitar profundidade para evitar busca muito longa
        level = root.replace(diretorio_atual, '').count(os.sep)
        if level >= 2:
            dirs[:] = []  # Não descer mais níveis
            continue
            
        for nome in nomes_possiveis:
            if nome in files:
                caminho = os.path.join(root, nome)
                print(f"✅ Planilha encontrada (busca recursiva): {caminho}")
                return caminho
    
    # Se não encontrou, retorna o nome padrão
    print("⚠️ Planilha não encontrada, usando nome padrão")
    return "operacoes.xlsx"


# --- ROTAS DE CÁLCULO (MANTIDAS EXATAMENTE COMO NO SEU CÓDIGO) ---
@calculadora_bp.route("/calcular_vna", methods=["POST"])
def calcular_vna():
    try:
        data = request.get_json()
        vne = float(data.get("vne", 0))
        ipca_emissao = float(data.get("ipca_emissao", 0))

        # 🔹 Alteração feita aqui
        ipca_atual = data.get("ipca_atual")
        if ipca_atual is None or ipca_atual == 0:
            ipca_atual = buscar_ipca_atual()
        else:
            ipca_atual = float(ipca_atual)

        if vne <= 0 or ipca_emissao <= 0 or ipca_atual <= 0:
            return jsonify({
                "success": False,
                "error": "Todos os valores devem ser maiores que zero"
            }), 400

        fator_correcao = ipca_atual / ipca_emissao
        vna_calculado = vne * fator_correcao
        data_calculo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        try:
            if not os.path.exists(PLANILHA_PU_FILE):
                return jsonify({
                    "success": True,
                    "vna_calculado": round(vna_calculado, 8),
                    "fator_correcao": round(fator_correcao, 8),
                    "data_calculo": data_calculo,
                    "salvamento_sucesso": False,
                    "erro_salvamento": f"Arquivo da planilha {PLANILHA_PU_FILE} não encontrado."
                })
            
            salvamento_sucesso = save_calculation_to_spreadsheet(
                PLANILHA_PU_FILE,
                vna_calculado,
                fator_correcao,
                data_calculo
            )
            
            # Salvar no banco de dados SQLite
            try:
                salvar_calculo_vna(vne, ipca_emissao, ipca_atual, vna_calculado, fator_correcao)
            except Exception as db_error:
                print(f"Erro ao salvar no banco de dados: {db_error}")

            return jsonify({
                "success": True,
                "vna_calculado": round(vna_calculado, 8),
                "fator_correcao": round(fator_correcao, 8),
                "ipca_atual": round(ipca_atual, 8),
                "data_calculo": data_calculo,
                "salvamento_sucesso": salvamento_sucesso
            })

        except Exception as e:
            return jsonify({
                "success": True,
                "vna_calculado": round(vna_calculado, 8),
                "fator_correcao": round(fator_correcao, 8),
                "ipca_atual": round(ipca_atual, 8),
                "data_calculo": data_calculo,
                "salvamento_sucesso": False,
                "erro_salvamento": str(e)
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao calcular VNA: {str(e)}"
        }), 500


@calculadora_bp.route("/calcular_pu_par", methods=["POST"])
def calcular_pu_par_endpoint():
    try:
        data = request.get_json()
        vna = float(data.get("vna", 0))
        taxa_juros = float(data.get("taxa_juros", 0))
        dias_uteis = int(data.get("dias_uteis", 0))
        base_calculo = int(data.get("base_calculo", 252))
        if vna <= 0:
            return jsonify({"success": False, "error": "VNA deve ser maior que zero"}), 400
        if taxa_juros < 0:
            return jsonify({"success": False, "error": "Taxa de juros deve ser maior ou igual a zero"}), 400
        if dias_uteis < 0:
            return jsonify({"success": False, "error": "Dias úteis deve ser maior ou igual a zero"}), 400
        if base_calculo not in [252, 360, 365]:
            return jsonify({"success": False, "error": "Base de cálculo deve ser 252, 360 ou 365"}), 400
        pu_par = calcular_pu_par(vna, taxa_juros, dias_uteis, base_calculo)
        if pu_par is None:
            return jsonify({"success": False, "error": "Erro no cálculo do PU PAR"}), 500
        data_calculo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            if not os.path.exists(PLANILHA_PU_FILE):
                return jsonify({"success": True, "pu_par": pu_par, "data_calculo": data_calculo, "salvamento_sucesso": False, "erro_salvamento": f"Arquivo da planilha {PLANILHA_PU_FILE} não encontrado."})
            salvamento_sucesso = save_pu_par_to_spreadsheet(PLANILHA_PU_FILE, vna, taxa_juros, dias_uteis, base_calculo, pu_par, data_calculo)
            
            # Salvar no banco de dados SQLite
            try:
                salvar_pu_par(vna, taxa_juros, dias_uteis, base_calculo, pu_par)
            except Exception as db_error:
                print(f"Erro ao salvar no banco de dados: {db_error}")
            
            return jsonify({"success": True, "pu_par": pu_par, "data_calculo": data_calculo, "salvamento_sucesso": salvamento_sucesso})
        except Exception as e:
            return jsonify({"success": True, "pu_par": pu_par, "data_calculo": data_calculo, "salvamento_sucesso": False, "erro_salvamento": str(e)})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao calcular PU PAR: {str(e)}"}), 500


# ENDPOINT MODIFICADO: calcular_pu_operacao com integração ao buscar_ativo
@calculadora_bp.route("/calcular_pu_operacao", methods=["POST"])
def calcular_pu_operacao_endpoint():
    try:
        data = request.get_json()
        
        # NOVA FUNCIONALIDADE: Verificar se foi fornecido código IF
        codigo_if = data.get("codigo_if")
        
        # Parâmetros originais
        taxa_mercado = data.get("taxa_mercado")
        base_calculo = int(data.get("base_calculo", 252))
        fluxos = data.get("fluxos", [])
        
        # Informações do ativo (para retorno)
        info_ativo = None
        
        # INTEGRAÇÃO: Se código IF foi fornecido, buscar dados do ativo
        if codigo_if and codigo_if.strip():
            try:
                caminho_planilha = encontrar_planilha()  # CORREÇÃO: Usar função que encontra automaticamente
                identificador = AssetIdentifier()
                resultado_busca = identificador.buscar_por_codigo_if(caminho_planilha, codigo_if)
                
                if resultado_busca.get("success") and resultado_busca.get("matches"):
                    ativo_data = resultado_busca["matches"][0]["valores"]
                    
                    # Extrair dados relevantes do ativo (baseado na estrutura da planilha)
                    nome_ativo = ativo_data[0] if len(ativo_data) > 0 else "N/A"
                    pu_emissao = ativo_data[20] if len(ativo_data) > 20 and ativo_data[20] is not None else 1000000
                    taxa_ativo = ativo_data[31] if len(ativo_data) > 31 and ativo_data[31] is not None else None
                    indexador = ativo_data[29] if len(ativo_data) > 29 else "N/A"
                    
                    # Usar taxa do ativo se não foi fornecida taxa de mercado
                    if taxa_mercado is None and taxa_ativo is not None:
                        taxa_mercado = float(taxa_ativo)
                    
                    # Criar fluxos padrão se não foram fornecidos
                    if not fluxos:
                        fluxos = [{"dias_uteis": 252, "valor": float(pu_emissao)}]
                    
                    # Preparar informações do ativo para retorno
                    info_ativo = {
                        "codigo_if": codigo_if,
                        "nome": nome_ativo,
                        "pu_emissao": float(pu_emissao),
                        "taxa": float(taxa_ativo) if taxa_ativo is not None else None,
                        "indexador": indexador
                    }
                    
            except Exception as e:
                # Se houver erro na busca, continuar com os dados fornecidos manualmente
                print(f"Erro ao buscar ativo {codigo_if}: {str(e)}")
        
        # Validações originais (mantidas)
        if taxa_mercado is None:
            return jsonify({"success": False, "error": "Taxa de mercado deve ser fornecida"}), 400
        
        taxa_mercado = float(taxa_mercado)
        if taxa_mercado < 0:
            return jsonify({"success": False, "error": "Taxa de mercado deve ser maior ou igual a zero"}), 400
        if base_calculo not in [252, 360, 365]:
            return jsonify({"success": False, "error": "Base de cálculo deve ser 252, 360 ou 365"}), 400
        if not fluxos:
            return jsonify({"success": False, "error": "Pelo menos um fluxo de pagamento deve ser fornecido"}), 400
        
        for i, fluxo in enumerate(fluxos):
            if "dias_uteis" not in fluxo or "valor" not in fluxo:
                return jsonify({"success": False, "error": f"Fluxo {i+1} deve conter dias_uteis e valor"}), 400
            try:
                fluxo["dias_uteis"] = int(fluxo["dias_uteis"])
                fluxo["valor"] = float(fluxo["valor"])
            except ValueError:
                return jsonify({"success": False, "error": f"Valores inválidos no fluxo {i+1}"}), 400
        
        # Cálculo original (mantido)
        pu_operacao = calcular_pu_operacao(taxa_mercado, base_calculo, fluxos)
        if pu_operacao is None:
            return jsonify({"success": False, "error": "Erro no cálculo do PU Operação"}), 500
        
        data_calculo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Salvamento original (mantido)
        try:
            if not os.path.exists(PLANILHA_PU_FILE):
                response_data = {
                    "success": True, 
                    "pu_operacao": pu_operacao, 
                    "data_calculo": data_calculo, 
                    "salvamento_sucesso": False, 
                    "erro_salvamento": f"Arquivo da planilha {PLANILHA_PU_FILE} não encontrado."
                }
                if info_ativo:
                    response_data["info_ativo"] = info_ativo
                return jsonify(response_data)
            
            salvamento_sucesso = save_pu_operacao_to_spreadsheet(PLANILHA_PU_FILE, taxa_mercado, base_calculo, fluxos, pu_operacao, data_calculo)
            
            # Salvar no banco de dados SQLite
            try:
                codigo_if_db = info_ativo.get('codigo_if') if info_ativo else None
                nome_ativo_db = info_ativo.get('nome') if info_ativo else None
                indexador_db = info_ativo.get('indexador') if info_ativo else None
                emissor_db = None
                data_vencimento_db = None
                
                salvar_pu_operacao(
                    codigo_if_db, nome_ativo_db, taxa_mercado, base_calculo, 
                    pu_operacao, indexador_db, emissor_db, data_vencimento_db
                )
            except Exception as db_error:
                print(f"Erro ao salvar no banco de dados: {db_error}")
            
            response_data = {
                "success": True, 
                "pu_operacao": pu_operacao, 
                "data_calculo": data_calculo, 
                "salvamento_sucesso": salvamento_sucesso
            }
            if info_ativo:
                response_data["info_ativo"] = info_ativo
            return jsonify(response_data)
            
        except Exception as e:
            response_data = {
                "success": True, 
                "pu_operacao": pu_operacao, 
                "data_calculo": data_calculo, 
                "salvamento_sucesso": False, 
                "erro_salvamento": str(e)
            }
            if info_ativo:
                response_data["info_ativo"] = info_ativo
            return jsonify(response_data)
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao calcular PU Operação: {str(e)}"}), 500


@calculadora_bp.route("/aplicar_filtros", methods=["POST"])
def aplicar_filtros_endpoint():
    try:
        data = request.get_json()
        taxas_input = data.get("taxas", "")
        if not taxas_input:
            return jsonify({"success": False, "error": "Lista de taxas não fornecida"}), 400
        try:
            taxas = [float(x.strip()) for x in taxas_input.split(",") if x.strip()]
        except ValueError:
            return jsonify({"success": False, "error": "Formato inválido de taxas. Use números separados por vírgula"}), 400
        if len(taxas) < 2:
            return jsonify({"success": False, "error": "Pelo menos duas taxas devem ser fornecidas"}), 400
        resultado = aplicar_filtros_estatisticos(taxas)
        if resultado is None:
            return jsonify({"success": False, "error": "Erro na aplicação dos filtros estatísticos"}), 500
        data_calculo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            if not os.path.exists(PLANILHA_PU_FILE):
                return jsonify({"success": True, "resultado": resultado, "data_calculo": data_calculo, "salvamento_sucesso": False, "erro_salvamento": f"Arquivo da planilha {PLANILHA_PU_FILE} não encontrado."})
            salvamento_sucesso = save_filtros_estatisticos_to_spreadsheet(PLANILHA_PU_FILE, taxas, resultado, data_calculo)
            return jsonify({"success": True, "resultado": resultado, "data_calculo": data_calculo, "salvamento_sucesso": salvamento_sucesso})
        except Exception as e:
            return jsonify({"success": True, "resultado": resultado, "data_calculo": data_calculo, "salvamento_sucesso": False, "erro_salvamento": str(e)})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao aplicar filtros: {str(e)}"}), 500


# --- ROTAS DO IDENTIFICADOR DE ATIVOS (MANTIDAS EXATAMENTE COMO NO SEU CÓDIGO) ---
@calculadora_bp.route("/ler_celula", methods=["POST"])
def ler_celula():
    try:
        data = request.get_json()
        file_path = data.get("file_path")
        sheet_name = data.get("sheet_name")
        cell_address = data.get("cell_address")
        if not all([file_path, sheet_name, cell_address]):
            return jsonify({"success": False, "error": "Parâmetros obrigatórios: file_path, sheet_name, cell_address"}), 400
        identificador = AssetIdentifier()
        resultado = identificador.read_cell_value(file_path, sheet_name, cell_address)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao ler célula: {str(e)}"}), 500


@calculadora_bp.route("/buscar_ativo", methods=["POST"])
def buscar_ativo():
    try:
        data = request.get_json()
        codigo_if = data.get("search_value")
        if not codigo_if:
            return jsonify({"success": False, "error": "Código IF não fornecido."}), 400

        caminho_planilha = encontrar_planilha()  # CORREÇÃO: Usar função que encontra automaticamente
        identificador = AssetIdentifier()
        resultado = identificador.buscar_por_codigo_if(caminho_planilha, codigo_if)
        return jsonify(resultado)

    except Exception as e:
        print(f"Erro ao buscar ativo: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao buscar ativo: {str(e)}"}), 500


# ROTA PARA "LISTAR ABAS"
@calculadora_bp.route("/listar_abas", methods=["POST"])
def listar_abas():
    """Endpoint para listar abas."""
    try:
        data = request.get_json()
       
        # CORREÇÃO: Chamando a função com o nome exato do seu arquivo: 'get_sheet_info' (singular)
        result = AssetIdentifier.get_sheet_info(
            file_path=data.get("file_path")
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao listar abas: {str(e)}"}), 500


# ROTA PARA "LER COLUNA"
@calculadora_bp.route("/ler_coluna", methods=["POST"])
def ler_coluna():
    """Endpoint para ler coluna."""
    try:
        data = request.get_json()
        
        # CORREÇÃO: Chamando a função com o nome exato do seu arquivo: 'read_column_values' (singular)
        result = AssetIdentifier.read_column_values(
            file_path=data.get("file_path"),
            sheet_name=data.get("sheet_name"),
            column=data.get("column"),
            start_row=data.get("start_row", 1),
            end_row=data.get("end_row")
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao ler coluna: {str(e)}"}), 500




# --- ROTAS PARA CADASTRO DE ATIVOS ---

# Arquivo para armazenar os ativos cadastrados
DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ATIVOS_FILE = os.path.join(DIRETORIO_RAIZ, "ativos_cadastrados.json")

def carregar_ativos():
    """Carrega a lista de ativos do arquivo JSON"""
    try:
        if os.path.exists(ATIVOS_FILE):
            with open(ATIVOS_FILE, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        return []
    except Exception as e:
        print(f"Erro ao carregar ativos: {e}")
        return []

def salvar_ativos(ativos):
    """Salva a lista de ativos no arquivo JSON"""
    try:
        with open(ATIVOS_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(ativos, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"Erro ao salvar ativos: {e}")
        return False

@calculadora_bp.route("/cadastrar_ativo", methods=["POST"])
def cadastrar_ativo():
    """Endpoint para cadastrar um novo ativo com campos expandidos"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        campos_obrigatorios = ["codigo_if", "nome", "emissor"]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "error": f"Campo '{campo}' é obrigatório"
                }), 400
        
        # Carregar ativos existentes
        ativos = carregar_ativos()
        
        # Verificar se o código IF já existe
        for ativo in ativos:
            if ativo.get("codigo_if") == data.get("codigo_if"):
                return jsonify({
                    "success": False,
                    "error": "Código IF já existe no sistema"
                }), 400
        
        # Função auxiliar para converter valores numéricos
        def safe_float(value):
            try:
                return float(value) if value else None
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            try:
                return int(value) if value else None
            except (ValueError, TypeError):
                return None
        
        # Criar novo ativo com todos os campos
        novo_ativo = {
            "id": len(ativos) + 1,
            
            # Campos obrigatórios
            "codigo_if": data.get("codigo_if"),
            "nome": data.get("nome"),
            "emissor": data.get("emissor"),
            
            # Informações básicas
            "status": data.get("status", ""),
            "emissao": data.get("emissao", ""),
            "papel": data.get("papel", ""),
            "serie": data.get("serie", ""),
            
            # Agentes e participantes
            "escriturador": data.get("escriturador", ""),
            "agente_fiduciario": data.get("agente_fiduciario", ""),
            "coordenador_lider": data.get("coordenador_lider", ""),
            "cedente": data.get("cedente", ""),
            "investidor": data.get("investidor", ""),
            "estrutura": data.get("estrutura", ""),
            
            # Datas
            "data_emissao": data.get("data_emissao", ""),
            "data_vencimento": data.get("data_vencimento", ""),
            "data_final_distribuicao": data.get("data_final_distribuicao", ""),
            "data_resgate_antecipado": data.get("data_resgate_antecipado", ""),
            "data_primeira_integralizacao": data.get("data_primeira_integralizacao", ""),
            
            # Características financeiras
            "pu_emissao": safe_float(data.get("pu_emissao")),
            "taxa": safe_float(data.get("taxa")),
            "indexador": data.get("indexador", ""),
            "agio": safe_float(data.get("agio")),
            "taxa_flutuante": safe_float(data.get("taxa_flutuante")),
            "taxa_juros_pre_spread": safe_float(data.get("taxa_juros_pre_spread")),
            
            # Volumes e quantidades
            "qtd_emitida": safe_int(data.get("qtd_emitida")),
            "volume_emissao": safe_float(data.get("volume_emissao")),
            "qtd_integralizada": safe_int(data.get("qtd_integralizada")),
            "saldo_devedor": safe_float(data.get("saldo_devedor")),
            "isin": data.get("isin", ""),
            
            # Características operacionais
            "tipo_oferta": data.get("tipo_oferta", ""),
            "gestao": data.get("gestao", ""),
            "servicing": data.get("servicing", ""),
            "pagamento_juros": data.get("pagamento_juros", ""),
            "amortizacao": data.get("amortizacao", ""),
            "observacao": data.get("observacao", ""),
            
            # Campos de controle
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ativo": True
        }
        
        # Adicionar à lista
        ativos.append(novo_ativo)
        
        # Salvar no arquivo
        if salvar_ativos(ativos):
            return jsonify({
                "success": True,
                "message": "Ativo cadastrado com sucesso",
                "ativo": novo_ativo
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao salvar ativo no arquivo"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao cadastrar ativo: {str(e)}"
        }), 500

@calculadora_bp.route("/listar_ativos", methods=["GET"])
def listar_ativos():
    """Endpoint para listar todos os ativos cadastrados"""
    try:
        ativos = carregar_ativos()
        
        # Filtrar apenas ativos ativos
        ativos_ativos = [ativo for ativo in ativos if ativo.get("ativo", True)]
        
        return jsonify({
            "success": True,
            "ativos": ativos_ativos,
            "total": len(ativos_ativos)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao listar ativos: {str(e)}"
        }), 500

@calculadora_bp.route("/buscar_ativo/<codigo_if>", methods=["GET"])
def buscar_ativo_por_codigo(codigo_if):
    """Endpoint para buscar um ativo específico pelo código IF"""
    try:
        ativos = carregar_ativos()
        
        # Buscar ativo pelo código IF
        for ativo in ativos:
            if ativo.get("codigo_if") == codigo_if and ativo.get("ativo", True):
                return jsonify({
                    "success": True,
                    "ativo": ativo
                })
        
        return jsonify({
            "success": False,
            "error": "Ativo não encontrado"
        }), 404
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao buscar ativo: {str(e)}"
        }), 500

@calculadora_bp.route("/atualizar_ativo/<int:ativo_id>", methods=["PUT"])
def atualizar_ativo(ativo_id):
    """Endpoint para atualizar um ativo existente"""
    try:
        data = request.get_json()
        ativos = carregar_ativos()
        
        # Encontrar o ativo
        ativo_encontrado = None
        for i, ativo in enumerate(ativos):
            if ativo.get("id") == ativo_id:
                ativo_encontrado = i
                break
        
        if ativo_encontrado is None:
            return jsonify({
                "success": False,
                "error": "Ativo não encontrado"
            }), 404
        
        # Atualizar campos
        ativo_atual = ativos[ativo_encontrado]
        campos_atualizaveis = ["nome", "emissor", "pu_emissao", "taxa", "indexador"]
        
        for campo in campos_atualizaveis:
            if campo in data:
                if campo in ["pu_emissao", "taxa"] and data[campo] is not None:
                    ativo_atual[campo] = float(data[campo])
                else:
                    ativo_atual[campo] = data[campo]
        
        ativo_atual["data_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Salvar
        if salvar_ativos(ativos):
            return jsonify({
                "success": True,
                "message": "Ativo atualizado com sucesso",
                "ativo": ativo_atual
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao salvar alterações"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao atualizar ativo: {str(e)}"
        }), 500

@calculadora_bp.route("/excluir_ativo/<int:ativo_id>", methods=["DELETE"])
def excluir_ativo(ativo_id):
    """Endpoint para excluir (desativar) um ativo"""
    try:
        ativos = carregar_ativos()
        
        # Encontrar o ativo
        ativo_encontrado = None
        for i, ativo in enumerate(ativos):
            if ativo.get("id") == ativo_id:
                ativo_encontrado = i
                break
        
        if ativo_encontrado is None:
            return jsonify({
                "success": False,
                "error": "Ativo não encontrado"
            }), 404
        
        # Marcar como inativo ao invés de excluir
        ativos[ativo_encontrado]["ativo"] = False
        ativos[ativo_encontrado]["data_exclusao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Salvar
        if salvar_ativos(ativos):
            return jsonify({
                "success": True,
                "message": "Ativo excluído com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao salvar alterações"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao excluir ativo: {str(e)}"
        }), 500

# Funções listar_ativos duplicadas removidas - mantida apenas a primeira ocorrência na linha 627   
    
@calculadora_bp.route("/carregar_ativos_planilha", methods=["GET", "POST"])
def carregar_ativos_planilha():
    import openpyxl
    from datetime import datetime
    import os
    from flask import jsonify, request
    
    # Se for GET, retornar mensagem informativa
    if request.method == "GET":
        return jsonify({
            "success": False,
            "message": "Use POST para carregar ativos da planilha",
            "endpoint": "/carregar_ativos_planilha",
            "method": "POST"
        })

    try:
        file_path = "operacoes.xlsx"

        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": f"Arquivo {file_path} não encontrado."})

        workbook = openpyxl.load_workbook(file_path, data_only=True)
        
        # Usar a primeira aba (evita problemas com encoding do nome)
        sheet = workbook.worksheets[0]

        ativos = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[4]:  # Coluna E = Código IF
                continue

            ativo = {
                "codigo_if": row[4],           # Col E
                "nome": row[0],                # Col A - Operação - Apelido
                "emissor": row[16],            # Col Q - Emissor
                "status": row[1],              # Col B - Status
                "emissao": row[2],             # Col C - Emissão
                "papel": row[3],               # Col D - Papel
                "serie": row[5],               # Col F - Série
                "escriturador": row[6],        # Col G
                "agente_fiduciario": row[17],  # Col R
                "coordenador_lider": row[18],  # Col S
                "cedente": row[19],            # Col T
                "investidor": row[15],         # Col P
                "estrutura": row[14],          # Col O
                "data_emissao": row[7].strftime('%Y-%m-%d') if (row[7] and hasattr(row[7], 'strftime')) else (str(row[7]) if row[7] else None),  # Col H
                "data_vencimento": row[8].strftime('%Y-%m-%d') if (row[8] and hasattr(row[8], 'strftime')) else (str(row[8]) if row[8] else None),  # Col I
                "data_final_distribuicao": row[9].strftime('%Y-%m-%d') if (row[9] and hasattr(row[9], 'strftime')) else (str(row[9]) if row[9] else None),  # Col J
                "data_resgate_antecipado": row[10].strftime('%Y-%m-%d') if (row[10] and hasattr(row[10], 'strftime')) else (str(row[10]) if row[10] else None),  # Col K
                "data_primeira_integralizacao": row[12].strftime('%Y-%m-%d') if (row[12] and hasattr(row[12], 'strftime')) else (str(row[12]) if row[12] else None),  # Col M
                "pu_emissao": row[20],         # Col U
                "taxa": row[31],               # Col AF - Taxa de Juros Pré/Spread
                "indexador": row[29],          # Col AD
                "agio": row[21],               # Col V
                "taxa_flutuante": row[30],     # Col AE
                "qtd_emitida": row[22],        # Col W
                "volume_emissao": row[23],     # Col X
                "qtd_integralizada": row[24],  # Col Y
                "saldo_devedor": row[26],      # Col AA
                "isin": row[13],               # Col N
                "tipo_oferta": row[11],        # Col L
                "gestao": row[27],             # Col AB
                "servicing": row[28],          # Col AC
                "pagamento_juros": row[32],    # Col AG
                "amortizacao": row[33],        # Col AH
                "observacao": row[25],         # Col Z
                "data_cadastro": datetime.now().isoformat()
            }
            ativos.append(ativo)

        return jsonify({"success": True, "ativos": ativos})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@calculadora_bp.route("/status_planilha", methods=["GET"])
def status_planilha():
    """Endpoint para verificar status da planilha"""
    try:
        planilha_path = os.path.join(DIRETORIO_RAIZ, "operacoes.xlsx")
        
        if os.path.exists(planilha_path):
            file_size = os.path.getsize(planilha_path)
            file_modified = os.path.getmtime(planilha_path)
            from datetime import datetime
            modified_date = datetime.fromtimestamp(file_modified).strftime('%d/%m/%Y %H:%M:%S')
            
            return jsonify({
                "success": True,
                "status": "disponível",
                "path": planilha_path,
                "size": f"{file_size / 1024:.2f} KB",
                "modified": modified_date
            })
        else:
            return jsonify({
                "success": True,
                "status": "não encontrada",
                "path": planilha_path
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao verificar status: {str(e)}"
        }), 500



# ============================================================================
# ROTAS PARA CALCULADORA DE JUROS
# ============================================================================

@calculadora_bp.route("/calcular_juros", methods=["POST"])
def calcular_juros_endpoint():
    """
    Endpoint para calcular juros de um ativo específico
    
    Request JSON:
    {
        "codigo_if": "22F1187231",
        "data": "2024-01-25"  (opcional, padrão: dia 25 do mês atual)
    }
    
    Response:
    {
        "sucesso": true,
        "codigo_if": "22F1187231",
        "data": "2024-01-25",
        "vna": 1234.56789012,
        "porcentagem": 0.004083,
        "juros_calculado": 5.04321098,
        "erro": null
    }
    """
    try:
        data = request.get_json()
        codigo_if = data.get("codigo_if", "").strip()
        data_str = data.get("data")
        
        if not codigo_if:
            return jsonify({
                "sucesso": False,
                "erro": "Código IF é obrigatório"
            }), 400
        
        # Converter string de data se fornecida
        target_date = None
        if data_str:
            try:
                from datetime import datetime
                target_date = datetime.strptime(data_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({
                    "sucesso": False,
                    "erro": "Formato de data inválido. Use YYYY-MM-DD"
                }), 400
        
        # Usar o novo JurosCalculator que busca na planilha de Caracteristicas
        try:
            from src.juros_calculator import JurosCalculator as NovoJurosCalculator
            
            # Encontrar a planilha de características
            import glob
            planilha_path = None
            for arquivo in glob.glob(os.path.join(DIRETORIO_RAIZ, '*.xlsx')):
                if 'Caracter' in arquivo:
                    planilha_path = arquivo
                    break
            
            if planilha_path is None:
                return jsonify({
                    "sucesso": False,
                    "erro": "Planilha de características não encontrada"
                }), 404
            
            calc = NovoJurosCalculator(planilha_path)
            resultado = calc.calcular_juros(codigo_if)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "sucesso": False,
                "erro": f"Erro ao calcular juros: {str(e)}"
            }), 500
        
        # Converter resultado para formato esperado
        if resultado.get('success'):
            return jsonify({
                "sucesso": True,
                "codigo_if": resultado['codigo'],
                "emissao": resultado['emissao'],
                "taxa": resultado['taxa'],
                "juros_calculado": resultado['juros'],
                "data_calculo": resultado['data_calculo'],
                "erro": None
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "erro": resultado.get('error', 'Erro desconhecido')
            }), 400
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao calcular juros: {str(e)}"
        }), 500


@calculadora_bp.route("/calcular_juros_todos", methods=["POST"])
def calcular_juros_todos_endpoint():
    """
    Endpoint para calcular juros de todos os ativos
    
    Request JSON:
    {
        "data": "2024-01-25"  (opcional, padrão: dia 25 do mês atual)
    }
    
    Response:
    {
        "sucesso": true,
        "data": "2024-01-25",
        "total_ativos": 5,
        "ativos_calculados": 5,
        "resultados": {
            "22F1187231": { ... },
            "14J0107228": { ... }
        }
    }
    """
    try:
        data = request.get_json() or {}
        data_str = data.get("data")
        
        # Converter string de data se fornecida
        target_date = None
        if data_str:
            try:
                from datetime import datetime
                target_date = datetime.strptime(data_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({
                    "sucesso": False,
                    "erro": "Formato de data inválido. Use YYYY-MM-DD"
                }), 400
        
        # Encontrar a planilha
        planilha_path = None
        for possivel_path in [
            os.path.join(os.getcwd(), "planilha_pu.xlsx"),
            os.path.join(DIRETORIO_RAIZ, "planilha_pu.xlsx"),
            os.path.join(os.path.dirname(os.getcwd()), "planilha_pu.xlsx"),
        ]:
            if os.path.exists(possivel_path):
                planilha_path = possivel_path
                break
        
        if not planilha_path:
            return jsonify({
                "sucesso": False,
                "erro": "Arquivo planilha_pu.xlsx não encontrado"
            }), 404
        
        # Criar calculadora e calcular para todos
        calculadora = JurosCalculator(planilha_path)
        resultados = calculadora.calcular_juros_todos_ativos(target_date)
        calculadora.close()
        
        # Contar sucessos
        ativos_calculados = sum(1 for r in resultados.values() if r['sucesso'])
        
        from datetime import datetime
        data_calculo = target_date or datetime.now()
        
        resposta = {
            "sucesso": True,
            "data": data_calculo.strftime("%Y-%m-%d"),
            "data_calculo": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "total_ativos": len(resultados),
            "ativos_calculados": ativos_calculados,
            "resultados": resultados
        }
        
        return jsonify(resposta), 200
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao calcular juros: {str(e)}"
        }), 500


@calculadora_bp.route("/juros_historico", methods=["GET"])
def juros_historico():
    """
    Endpoint para obter histórico de cálculos de juros
    
    Query parameters:
    - codigo_if: Código IF do ativo (opcional)
    - limite: Número máximo de registros (padrão: 100)
    
    Response:
    {
        "sucesso": true,
        "total": 10,
        "registros": [
            {
                "id": 1,
                "codigo_if": "22F1187231",
                "data": "2024-01-25",
                "vna": 1234.56789012,
                "porcentagem": 0.004083,
                "juros_calculado": 5.04321098,
                "data_calculo": "2024-01-25 10:30:00"
            }
        ]
    }
    """
    try:
        codigo_if = request.args.get("codigo_if")
        limite = int(request.args.get("limite", 100))
        
        if not DATABASE_ENABLED:
            return jsonify({
                "sucesso": False,
                "erro": "Banco de dados não disponível"
            }), 503
        
        from src.database import obter_historico_juros
        registros = obter_historico_juros(codigo_if, limite)
        
        return jsonify({
            "sucesso": True,
            "total": len(registros),
            "registros": registros
        }), 200
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao obter histórico: {str(e)}"
        }), 500



# ============================================================================
# NOVO ENDPOINT: CALCULAR AMORTIZAÇÃO
# ============================================================================
# Fórmula: =TRUNCAR(G * PROCV(D; 'Amort TS'!G3:H140; 2; 0); 8)
# ============================================================================

@calculadora_bp.route("/calcular_amortizacao", methods=["POST"])
def calcular_amortizacao():
    """
    Endpoint para calcular amortização usando a fórmula:
    =TRUNCAR(valor_principal * PROCV(chave; 'Amort TS'!G3:H140; 2; 0); 8)
    
    Request JSON:
    {
        "valor_principal": 1234.56,
        "chave": "25/02/2026"
    }
    
    Response:
    {
        "success": true,
        "resultado": "123.12345678",
        "valor_principal": 1234.56,
        "chave": "25/02/2026",
        "porcentagem": 0.09987654
    }
    
    Erros possíveis:
    - 400: Parâmetros inválidos
    - 404: Planilha não encontrada
    - 500: Erro no cálculo
    """
    try:
        # Obter dados do JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Body JSON vazio"
            }), 400
        
        # Extrair parâmetros
        valor_principal = data.get("valor_principal")
        chave = data.get("chave")
        
        # Validar parâmetros obrigatórios
        if valor_principal is None:
            return jsonify({
                "success": False,
                "error": "Parâmetro 'valor_principal' é obrigatório"
            }), 400
        
        if chave is None or chave == '':
            return jsonify({
                "success": False,
                "error": "Parâmetro 'chave' é obrigatório"
            }), 400
        
        # Validar tipo de valor_principal
        try:
            valor_principal = float(valor_principal)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": f"valor_principal deve ser um número válido, recebido: {valor_principal}"
            }), 400
        
        # Validar tipo de chave
        chave = str(chave).strip()
        
        # Encontrar a planilha
        planilha_path = None
        caminhos_possiveis = [
            os.path.join(os.getcwd(), "planilha_pu.xlsx"),
            os.path.join(DIRETORIO_RAIZ, "planilha_pu.xlsx"),
            os.path.join(os.path.dirname(os.getcwd()), "planilha_pu.xlsx"),
            PLANILHA_PU_FILE
        ]
        
        for caminho in caminhos_possiveis:
            if os.path.exists(caminho):
                planilha_path = caminho
                break
        
        if not planilha_path:
            return jsonify({
                "success": False,
                "error": "Arquivo planilha_pu.xlsx não encontrado"
            }), 404
        
        # Importar a calculadora de amortização
        try:
            from src.amortizacao_calculator import AmortizacaoCalculator
        except ImportError:
            return jsonify({
                "success": False,
                "error": "Módulo AmortizacaoCalculator não disponível"
            }), 500
        
        # Criar calculadora e calcular
        try:
            calculadora = AmortizacaoCalculator(planilha_path)
            resultado = calculadora.calcular_amortizacao(valor_principal, chave)
            calculadora.close()
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Erro ao inicializar calculadora: {str(e)}"
            }), 500
        
        # Verificar se o cálculo foi bem-sucedido
        if not resultado['sucesso']:
            return jsonify({
                "success": False,
                "error": resultado['erro']
            }), 400
        
        # Retornar resultado com sucesso
        resposta = {
            "success": True,
            "resultado": resultado['resultado'],
            "valor_principal": valor_principal,
            "chave": chave,
            "porcentagem": resultado['porcentagem'],
            "data_calculo": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        return jsonify(resposta), 200
        
    except Exception as e:
        print(f"❌ Erro inesperado em /calcular_amortizacao: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": f"Erro ao calcular amortização: {str(e)}"
        }), 500


# Rota para carregar histórico de cálculos de juros