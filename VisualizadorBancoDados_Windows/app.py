import os
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Habilitar CORS
CORS(app)

# Inicializar banco de dados
try:
    from src.database import init_database
    init_database()
    print("[OK] Banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"[AVISO] Erro ao inicializar banco de dados: {e}")
    print("[AVISO] Sistema continuará funcionando sem banco de dados")

# Inicializar scheduler de juros
try:
    import os
    planilha_path = os.path.join(os.path.dirname(__file__), "planilha_pu.xlsx")
    
    # Procurar a planilha em diferentes locais
    if not os.path.exists(planilha_path):
        for possivel_path in [
            os.path.join(os.getcwd(), "planilha_pu.xlsx"),
            os.path.join(os.path.dirname(os.getcwd()), "planilha_pu.xlsx"),
        ]:
            if os.path.exists(possivel_path):
                planilha_path = possivel_path
                break
    
    if os.path.exists(planilha_path):
        from src.scheduler_juros import inicializar_scheduler 
        scheduler = inicializar_scheduler(planilha_path, db_enabled=True)
        scheduler.agendar_calculo_dia_25(hora=10, minuto=0)  # Executar às 10:00 do dia 25
        print("[OK] Scheduler de juros inicializado com sucesso!")
    else:
        print("[AVISO] Planilha planilha_pu.xlsx não encontrada. Scheduler de juros desabilitado.")
except Exception as e:
    print(f"[AVISO] Erro ao inicializar scheduler de juros: {e}")
    print("[AVISO] Sistema continuará funcionando sem agendamento automático")

# Importar e registrar blueprints
try:
    from src.routes.calculadora_bp import calculadora_bp
    app.register_blueprint(calculadora_bp, url_prefix='')
    print("[OK] Blueprint calculadora registrado!")
except Exception as e:
    print(f"[ERRO] Erro ao importar calculadora_bp: {e}")
    import traceback
    traceback.print_exc()

try:
    from src.routes.database_bp import database_bp
    app.register_blueprint(database_bp, url_prefix='/database')
    print("[OK] Blueprint database registrado!")
except Exception as e:
    print(f"[AVISO] Erro ao importar database_bp: {e}")
    print("[AVISO] Visualizador do banco não estará disponível")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Erro ao carregar template: {e}"

@app.route('/test')
def test():
    return "Servidor Flask funcionando!"

@app.route('/health')
def health():
    return {"status": "ok", "message": "Sistema operacional"}

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[INICIANDO] SERVIDOR FLASK")
    print("="*60)
    print(f"[DIR] Diretório: {os.getcwd()}")
    print(f"[URL] URL: http://localhost:5003/")
    print(f"[BD] Banco: http://localhost:5003/database")
    print(f"[AGENDADOR] Agendador: Ativo (Dia 25 às 10:00)")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5003, debug=False, threaded=True, use_reloader=False)