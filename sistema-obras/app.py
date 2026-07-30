from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from flask import send_from_directory
import os
import io
import json

app = Flask(__name__)

# Configuração CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuração do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "obras.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos do banco de dados
class PessoaResponsavel(db.Model):
    __tablename__ = 'pessoa_responsavel'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(100))
    funcao = db.Column(db.String(100))
    email = db.Column(db.String(120))
    cpf = db.Column(db.String(14))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com obras
    obras = db.relationship('Obra', backref='responsavel', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'contato': self.contato,
            'funcao': self.funcao,
            'email': self.email,
            'cpf': self.cpf,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

class Obra(db.Model):
    __tablename__ = 'obra'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_projeto = db.Column(db.String(50))
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    endereco = db.Column(db.String(300))
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date)
    data_prevista_fim = db.Column(db.Date)
    data_inicio_real = db.Column(db.Date)  # Data início real da construção
    data_termino_dedicacao = db.Column(db.Date)  # Data de término e dedicação
    orcamento = db.Column(db.Float)
    status = db.Column(db.String(50), default='Em Planejamento')
    responsavel_id = db.Column(db.Integer, db.ForeignKey('pessoa_responsavel.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com relatórios mensais
    relatorios = db.relationship('RelatorioMensal', backref='obra', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_projeto': self.numero_projeto,
            'nome': self.nome,
            'descricao': self.descricao,
            'endereco': self.endereco,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'data_prevista_fim': self.data_prevista_fim.isoformat() if self.data_prevista_fim else None,
            'data_inicio_real': self.data_inicio_real.isoformat() if self.data_inicio_real else None,
            'data_termino_dedicacao': self.data_termino_dedicacao.isoformat() if self.data_termino_dedicacao else None,
            'orcamento': self.orcamento,
            'status': self.status,
            'responsavel_id': self.responsavel_id,
            'responsavel': self.responsavel.to_dict() if self.responsavel else None,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ultimo_relatorio': self.get_ultimo_relatorio()
        }
    
    def get_ultimo_relatorio(self):
        ultimo = RelatorioMensal.query.filter_by(obra_id=self.id).order_by(RelatorioMensal.data_relatorio.desc()).first()
        return ultimo.to_dict() if ultimo else None

class RelatorioMensal(db.Model):
    __tablename__ = 'relatorio_mensal'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obra.id'), nullable=False)
    data_relatorio = db.Column(db.Date, nullable=False)  # Último dia útil do mês
    valor_gasto = db.Column(db.Float, default=0.0)
    valor_comprometido = db.Column(db.Float, default=0.0)
    data_inicio_seguro = db.Column(db.Date)
    data_vencimento_seguro = db.Column(db.Date)
    evolucao_obra_percent = db.Column(db.Float, default=0.0)  # Evolução da obra em %
    comentarios = db.Column(db.Text)  # Serviços realizados no período
    relatos_lideranca = db.Column(db.Text)  # Visitas e vistorias
    foto1_url = db.Column(db.String(255))
    foto2_url = db.Column(db.String(255))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    aprovado = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'obra_id': self.obra_id,
            'data_relatorio': self.data_relatorio.isoformat() if self.data_relatorio else None,
            'valor_gasto': self.valor_gasto,
            'valor_comprometido': self.valor_comprometido,
            'data_inicio_seguro': self.data_inicio_seguro.isoformat() if self.data_inicio_seguro else None,
            'data_vencimento_seguro': self.data_vencimento_seguro.isoformat() if self.data_vencimento_seguro else None,
            'evolucao_obra_percent': self.evolucao_obra_percent,
            'comentarios': self.comentarios,
            'relatos_lideranca': self.relatos_lideranca,
            'foto1_url': self.foto1_url,
            'foto2_url': self.foto2_url,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'aprovado': self.aprovado
        }

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso não encontrado'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Requisição inválida'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Rotas para Dashboard
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        total_obras = Obra.query.count()
        total_responsaveis = PessoaResponsavel.query.count()
        
        # Contar obras por status
        obras_em_andamento = Obra.query.filter(
            (Obra.status == 'Em Andamento') | 
            (Obra.status == 'Em Planejamento')
        ).count()
        
        obras_concluidas = Obra.query.filter(Obra.status == 'Concluída').count()
        
        # Obras com atraso (data prevista passou e não foi concluída)
        hoje = date.today()
        obras_atrasadas = Obra.query.filter(
            Obra.data_prevista_fim < hoje,
            Obra.status != 'Concluída'
        ).count()
        
        # Valor total dos orçamentos
        valor_total = db.session.query(db.func.sum(Obra.orcamento)).scalar() or 0
        
        # Valor total gasto (do último relatório de cada obra)
        valor_total_gasto = 0
        valor_total_comprometido = 0
        
        obras = Obra.query.all()
        for obra in obras:
            ultimo_relatorio = RelatorioMensal.query.filter_by(obra_id=obra.id).order_by(RelatorioMensal.data_relatorio.desc()).first()
            if ultimo_relatorio:
                valor_total_gasto += ultimo_relatorio.valor_gasto or 0
                valor_total_comprometido += ultimo_relatorio.valor_comprometido or 0
        
        # Evolução média das obras
        evolucao_media = 0
        total_relatorios = RelatorioMensal.query.count()
        if total_relatorios > 0:
            soma_evolucao = db.session.query(db.func.sum(RelatorioMensal.evolucao_obra_percent)).scalar() or 0
            evolucao_media = soma_evolucao / total_obras if total_obras > 0 else 0
        
        return jsonify({
            'total_obras': total_obras,
            'total_responsaveis': total_responsaveis,
            'obras_em_andamento': obras_em_andamento,
            'obras_concluidas': obras_concluidas,
            'obras_atrasadas': obras_atrasadas,
            'valor_total_orcamentos': valor_total,
            'valor_total_gasto': valor_total_gasto,
            'valor_total_comprometido': valor_total_comprometido,
            'evolucao_media': round(evolucao_media, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas para Pessoas Responsáveis
@app.route('/api/responsibles', methods=['GET'])
def get_responsibles():
    try:
        responsibles = PessoaResponsavel.query.all()
        return jsonify([r.to_dict() for r in responsibles])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responsibles/<int:id>', methods=['GET'])
def get_responsible(id):
    try:
        responsible = PessoaResponsavel.query.get_or_404(id)
        return jsonify(responsible.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responsibles', methods=['POST'])
def create_responsible():
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        responsible = PessoaResponsavel(
            nome=data['nome'],
            contato=data.get('contato'),
            funcao=data.get('funcao'),
            email=data.get('email'),
            cpf=data.get('cpf')
        )
        
        db.session.add(responsible)
        db.session.commit()
        
        return jsonify(responsible.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/responsibles/<int:id>', methods=['PUT'])
def update_responsible(id):
    try:
        responsible = PessoaResponsavel.query.get_or_404(id)
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        responsible.nome = data['nome']
        responsible.contato = data.get('contato')
        responsible.funcao = data.get('funcao')
        responsible.email = data.get('email')
        responsible.cpf = data.get('cpf')
        
        db.session.commit()
        
        return jsonify(responsible.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/responsibles/<int:id>', methods=['DELETE'])
def delete_responsible(id):
    try:
        responsible = PessoaResponsavel.query.get_or_404(id)
        
        # Verificar se há obras associadas
        if responsible.obras:
            return jsonify({'error': 'Não é possível excluir responsável com obras associadas'}), 400
        
        db.session.delete(responsible)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Obras
@app.route('/api/works', methods=['GET'])
def get_works():
    try:
        # Parâmetros de filtro
        status = request.args.get('status')
        responsavel_id = request.args.get('responsavel_id')
        
        query = Obra.query
        
        if status:
            query = query.filter(Obra.status == status)
        
        if responsavel_id:
            query = query.filter(Obra.responsavel_id == responsavel_id)
        
        works = query.order_by(Obra.data_cadastro.desc()).all()
        return jsonify([w.to_dict() for w in works])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/works/<int:id>', methods=['GET'])
def get_work(id):
    try:
        work = Obra.query.get_or_404(id)
        return jsonify(work.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/works', methods=['POST'])
def create_work():
    try:
        data = request.get_json()
        
        required_fields = ['nome', 'data_inicio', 'responsavel_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Verificar se o responsável existe
        responsavel = PessoaResponsavel.query.get(data['responsavel_id'])
        if not responsavel:
            return jsonify({'error': 'Responsável não encontrado'}), 400
        
        # Converter strings de data para objetos datetime.date
        try:
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data de início inválido. Use YYYY-MM-DD'}), 400
        
        data_fim = None
        if data.get('data_fim'):
            try:
                data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%d').date()
                if data_fim < data_inicio:
                    return jsonify({'error': 'Data de fim não pode ser anterior à data de início'}), 400
            except ValueError:
                return jsonify({'error': 'Formato de data de fim inválido. Use YYYY-MM-DD'}), 400
        
        data_prevista_fim = None
        if data.get('data_prevista_fim'):
            try:
                data_prevista_fim = datetime.strptime(data['data_prevista_fim'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data prevista de fim inválido. Use YYYY-MM-DD'}), 400
        
        data_inicio_real = None
        if data.get('data_inicio_real'):
            try:
                data_inicio_real = datetime.strptime(data['data_inicio_real'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data início real inválido. Use YYYY-MM-DD'}), 400
        
        data_termino_dedicacao = None
        if data.get('data_termino_dedicacao'):
            try:
                data_termino_dedicacao = datetime.strptime(data['data_termino_dedicacao'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data término dedicação inválido. Use YYYY-MM-DD'}), 400
        
        work = Obra(
            numero_projeto=data.get('numero_projeto'),
            nome=data['nome'],
            descricao=data.get('descricao'),
            endereco=data.get('endereco'),
            data_inicio=data_inicio,
            data_fim=data_fim,
            data_prevista_fim=data_prevista_fim,
            data_inicio_real=data_inicio_real,
            data_termino_dedicacao=data_termino_dedicacao,
            orcamento=data.get('orcamento'),
            status=data.get('status', 'Em Planejamento'),
            responsavel_id=data['responsavel_id']
        )
        
        db.session.add(work)
        db.session.commit()
        
        return jsonify(work.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/works/<int:id>', methods=['PUT'])
def update_work(id):
    try:
        work = Obra.query.get_or_404(id)
        data = request.get_json()
        
        required_fields = ['nome', 'data_inicio', 'responsavel_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Verificar se o responsável existe
        responsavel = PessoaResponsavel.query.get(data['responsavel_id'])
        if not responsavel:
            return jsonify({'error': 'Responsável não encontrado'}), 400
        
        # Converter strings de data para objetos datetime.date
        try:
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data de início inválido. Use YYYY-MM-DD'}), 400
        
        data_fim = None
        if data.get('data_fim'):
            try:
                data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%d').date()
                if data_fim < data_inicio:
                    return jsonify({'error': 'Data de fim não pode ser anterior à data de início'}), 400
            except ValueError:
                return jsonify({'error': 'Formato de data de fim inválido. Use YYYY-MM-DD'}), 400
        
        data_prevista_fim = None
        if data.get('data_prevista_fim'):
            try:
                data_prevista_fim = datetime.strptime(data['data_prevista_fim'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data prevista de fim inválido. Use YYYY-MM-DD'}), 400
        
        data_inicio_real = None
        if data.get('data_inicio_real'):
            try:
                data_inicio_real = datetime.strptime(data['data_inicio_real'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data início real inválido. Use YYYY-MM-DD'}), 400
        
        data_termino_dedicacao = None
        if data.get('data_termino_dedicacao'):
            try:
                data_termino_dedicacao = datetime.strptime(data['data_termino_dedicacao'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data término dedicação inválido. Use YYYY-MM-DD'}), 400
        
        work.numero_projeto = data.get('numero_projeto')
        work.nome = data['nome']
        work.descricao = data.get('descricao')
        work.endereco = data.get('endereco')
        work.data_inicio = data_inicio
        work.data_fim = data_fim
        work.data_prevista_fim = data_prevista_fim
        work.data_inicio_real = data_inicio_real
        work.data_termino_dedicacao = data_termino_dedicacao
        work.orcamento = data.get('orcamento')
        work.status = data.get('status', work.status)
        work.responsavel_id = data['responsavel_id']
        
        db.session.commit()
        
        return jsonify(work.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/works/<int:id>', methods=['DELETE'])
def delete_work(id):
    try:
        work = Obra.query.get_or_404(id)
        db.session.delete(work)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Relatórios Mensais
@app.route('/api/works/<int:obra_id>/reports', methods=['GET'])
def get_monthly_reports(obra_id):
    try:
        obra = Obra.query.get_or_404(obra_id)
        reports = RelatorioMensal.query.filter_by(obra_id=obra_id).order_by(RelatorioMensal.data_relatorio.desc()).all()
        return jsonify([r.to_dict() for r in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/works/<int:obra_id>/reports', methods=['POST'])
def create_monthly_report(obra_id):
    try:
        obra = Obra.query.get_or_404(obra_id)
        data = request.get_json()
        
        if not data or not data.get('data_relatorio'):
            return jsonify({'error': 'Data do relatório é obrigatória'}), 400
        
        try:
            data_relatorio = datetime.strptime(data['data_relatorio'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Verificar se já existe relatório para esta data
        existing = RelatorioMensal.query.filter_by(obra_id=obra_id, data_relatorio=data_relatorio).first()
        if existing:
            return jsonify({'error': 'Já existe um relatório para esta data'}), 400
        
        data_inicio_seguro = None
        if data.get('data_inicio_seguro'):
            try:
                data_inicio_seguro = datetime.strptime(data['data_inicio_seguro'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data início seguro inválido'}), 400
        
        data_vencimento_seguro = None
        if data.get('data_vencimento_seguro'):
            try:
                data_vencimento_seguro = datetime.strptime(data['data_vencimento_seguro'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data vencimento seguro inválido'}), 400
        
        report = RelatorioMensal(
            obra_id=obra_id,
            data_relatorio=data_relatorio,
            valor_gasto=data.get('valor_gasto', 0.0),
            valor_comprometido=data.get('valor_comprometido', 0.0),
            data_inicio_seguro=data_inicio_seguro,
            data_vencimento_seguro=data_vencimento_seguro,
            evolucao_obra_percent=data.get('evolucao_obra_percent', 0.0),
            comentarios=data.get('comentarios'),
            relatos_lideranca=data.get('relatos_lideranca'),
            foto1_url=data.get('foto1_url'),
            foto2_url=data.get('foto2_url')
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:id>', methods=['PUT'])
def update_monthly_report(id):
    try:
        report = RelatorioMensal.query.get_or_404(id)
        data = request.get_json()
        
        if data.get('data_relatorio'):
            try:
                report.data_relatorio = datetime.strptime(data['data_relatorio'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        if data.get('data_inicio_seguro'):
            try:
                report.data_inicio_seguro = datetime.strptime(data['data_inicio_seguro'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data início seguro inválido'}), 400
        
        if data.get('data_vencimento_seguro'):
            try:
                report.data_vencimento_seguro = datetime.strptime(data['data_vencimento_seguro'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data vencimento seguro inválido'}), 400
        
        report.valor_gasto = data.get('valor_gasto', report.valor_gasto)
        report.valor_comprometido = data.get('valor_comprometido', report.valor_comprometido)
        report.evolucao_obra_percent = data.get('evolucao_obra_percent', report.evolucao_obra_percent)
        report.comentarios = data.get('comentarios', report.comentarios)
        report.relatos_lideranca = data.get('relatos_lideranca', report.relatos_lideranca)
        report.foto1_url = data.get('foto1_url', report.foto1_url)
        report.foto2_url = data.get('foto2_url', report.foto2_url)
        report.aprovado = data.get('aprovado', report.aprovado)
        
        db.session.commit()
        
        return jsonify(report.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:id>', methods=['DELETE'])
def delete_monthly_report(id):
    try:
        report = RelatorioMensal.query.get_or_404(id)
        db.session.delete(report)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rota para gerar relatório de obra individual
@app.route('/api/reports/works/<int:id>', methods=['GET'])
def generate_work_report(id):
    try:
        work = Obra.query.get_or_404(id)
        relatorios = RelatorioMensal.query.filter_by(obra_id=id).order_by(RelatorioMensal.data_relatorio.desc()).all()
        
        # Criar um buffer em memória para o PDF
        buffer = io.BytesIO()
        
        # Criar o documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Centralizado
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        )
        
        # Título do relatório
        story.append(Paragraph("RELATÓRIO DE ACOMPANHAMENTO DE OBRA", title_style))
        story.append(Spacer(1, 20))
        
        # Informações da obra
        story.append(Paragraph("INFORMAÇÕES GERAIS DA OBRA", heading_style))
        
        # Criar tabela com informações da obra
        data = [
            ['Número do Projeto:', work.numero_projeto or 'Não informado'],
            ['Nome da Obra:', work.nome],
            ['Descrição:', work.descricao or 'Não informada'],
            ['Endereço:', work.endereco or 'Não informado'],
            ['Status:', work.status],
            ['Data de Início:', work.data_inicio.strftime('%d/%m/%Y')],
            ['Data Início Real:', work.data_inicio_real.strftime('%d/%m/%Y') if work.data_inicio_real else 'Não informada'],
            ['Data Prevista de Fim:', work.data_prevista_fim.strftime('%d/%m/%Y') if work.data_prevista_fim else 'Não definida'],
            ['Data de Término/Dedicação:', work.data_termino_dedicacao.strftime('%d/%m/%Y') if work.data_termino_dedicacao else 'Não concluída'],
            ['Orçamento:', f'R$ {work.orcamento:,.2f}' if work.orcamento else 'Não informado']
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Informações do responsável
        story.append(Paragraph("RESPONSÁVEL PELA OBRA", heading_style))
        
        resp_data = [
            ['Nome:', work.responsavel.nome],
            ['Função:', work.responsavel.funcao or 'Não informada'],
            ['Contato:', work.responsavel.contato or 'Não informado'],
            ['Email:', work.responsavel.email or 'Não informado'],
            ['CPF:', work.responsavel.cpf or 'Não informado']
        ]
        
        resp_table = Table(resp_data, colWidths=[2.5*inch, 4*inch])
        resp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(resp_table)
        story.append(Spacer(1, 30))
        
        # Relatórios mensais
        if relatorios:
            story.append(Paragraph("HISTÓRICO DE RELATÓRIOS MENSAIS", heading_style))
            
            for i, relatorio in enumerate(relatorios[:6]):  # Mostrar últimos 6 relatórios
                story.append(Paragraph(f"Relatório - {relatorio.data_relatorio.strftime('%m/%Y')}", subheading_style))
                
                rel_data = [
                    ['Data do Relatório:', relatorio.data_relatorio.strftime('%d/%m/%Y')],
                    ['Valor Gasto:', f'R$ {relatorio.valor_gasto:,.2f}'],
                    ['Valor Comprometido:', f'R$ {relatorio.valor_comprometido:,.2f}'],
                    ['Evolução da Obra:', f'{relatorio.evolucao_obra_percent}%'],
                    ['Data Início Seguro:', relatorio.data_inicio_seguro.strftime('%d/%m/%Y') if relatorio.data_inicio_seguro else 'Não informada'],
                    ['Data Venc. Seguro:', relatorio.data_vencimento_seguro.strftime('%d/%m/%Y') if relatorio.data_vencimento_seguro else 'Não informada'],
                    ['Status:', 'Aprovado' if relatorio.aprovado else 'Pendente']
                ]
                
                rel_table = Table(rel_data, colWidths=[2*inch, 3*inch])
                rel_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (1, 0), (1, -1), colors.lightcyan),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(rel_table)
                
                # Comentários e relatos
                if relatorio.comentarios:
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("<b>Serviços Realizados:</b>", styles['Normal']))
                    story.append(Paragraph(relatorio.comentarios, styles['Normal']))
                
                if relatorio.relatos_lideranca:
                    story.append(Spacer(1, 5))
                    story.append(Paragraph("<b>Relatos da Liderança:</b>", styles['Normal']))
                    story.append(Paragraph(relatorio.relatos_lideranca, styles['Normal']))
                
                story.append(Spacer(1, 20))
                
                # Page break a cada 2 relatórios
                if i > 0 and i % 2 == 1:
                    story.append(PageBreak())
        
        # Análise de cronograma
        story.append(Paragraph("ANÁLISE DE CRONOGRAMA", heading_style))
        
        hoje = date.today()
        analise_texto = []
        
        if work.data_termino_dedicacao:
            if work.data_inicio_real:
                duracao = (work.data_termino_dedicacao - work.data_inicio_real).days
            else:
                duracao = (work.data_termino_dedicacao - work.data_inicio).days
            analise_texto.append(f"• Obra concluída em {duracao} dias.")
            
            if work.data_prevista_fim:
                diferenca = (work.data_termino_dedicacao - work.data_prevista_fim).days
                if diferenca > 0:
                    analise_texto.append(f"• Obra finalizada com {diferenca} dias de atraso.")
                elif diferenca < 0:
                    analise_texto.append(f"• Obra finalizada com {abs(diferenca)} dias de antecedência.")
                else:
                    analise_texto.append("• Obra finalizada na data prevista.")
        else:
            data_ref = work.data_inicio_real if work.data_inicio_real else work.data_inicio
            duracao_atual = (hoje - data_ref).days
            analise_texto.append(f"• Obra em andamento há {duracao_atual} dias.")
            
            if work.data_prevista_fim:
                if hoje > work.data_prevista_fim:
                    atraso = (hoje - work.data_prevista_fim).days
                    analise_texto.append(f"• Obra está atrasada em {atraso} dias.")
                else:
                    restante = (work.data_prevista_fim - hoje).days
                    analise_texto.append(f"• Restam {restante} dias para a data prevista de conclusão.")
        
        # Análise financeira
        if relatorios:
            ultimo_relatorio = relatorios[0]
            if work.orcamento and ultimo_relatorio.valor_gasto:
                percentual_gasto = (ultimo_relatorio.valor_gasto / work.orcamento) * 100
                analise_texto.append(f"• Percentual do orçamento gasto: {percentual_gasto:.1f}%")
            
            if ultimo_relatorio.evolucao_obra_percent:
                analise_texto.append(f"• Evolução física da obra: {ultimo_relatorio.evolucao_obra_percent}%")
        
        for texto in analise_texto:
            story.append(Paragraph(texto, styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Rodapé
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.grey
        )
        
        story.append(Spacer(1, 50))
        story.append(Paragraph("Relatório gerado automaticamente pelo Sistema de Acompanhamento de Obras", footer_style))
        story.append(Paragraph(f"Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
        
        # Construir o PDF
        doc.build(story)
        
        # Preparar o buffer para envio
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'relatorio_obra_{work.id}_{work.nome.replace(" ", "_")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para gerar relatório geral de todas as obras
@app.route('/api/reports/general', methods=['GET'])
def generate_general_report():
    try:
        works = Obra.query.order_by(Obra.data_inicio.desc()).all()
        
        # Criar um buffer em memória para o PDF
        buffer = io.BytesIO()
        
        # Criar o documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Título do relatório
        story.append(Paragraph("RELATÓRIO GERAL DE ACOMPANHAMENTO DE OBRAS", title_style))
        story.append(Spacer(1, 20))
        
        # Estatísticas gerais
        total_obras = len(works)
        obras_concluidas = len([w for w in works if w.status == 'Concluída'])
        obras_em_andamento = len([w for w in works if w.status in ['Em Andamento', 'Em Planejamento']])
        valor_total_orcamento = sum([w.orcamento for w in works if w.orcamento]) or 0
        
        # Calcular valores dos últimos relatórios
        valor_total_gasto = 0
        valor_total_comprometido = 0
        evolucao_media = 0
        total_com_relatorio = 0
        
        for work in works:
            ultimo_relatorio = RelatorioMensal.query.filter_by(obra_id=work.id).order_by(RelatorioMensal.data_relatorio.desc()).first()
            if ultimo_relatorio:
                valor_total_gasto += ultimo_relatorio.valor_gasto or 0
                valor_total_comprometido += ultimo_relatorio.valor_comprometido or 0
                evolucao_media += ultimo_relatorio.evolucao_obra_percent or 0
                total_com_relatorio += 1
        
        if total_com_relatorio > 0:
            evolucao_media = evolucao_media / total_com_relatorio
        
        story.append(Paragraph("RESUMO EXECUTIVO", heading_style))
        
        resumo_data = [
            ['Total de Obras:', str(total_obras)],
            ['Obras Concluídas:', str(obras_concluidas)],
            ['Obras em Andamento:', str(obras_em_andamento)],
            ['Valor Total dos Orçamentos:', f'R$ {valor_total_orcamento:,.2f}'],
            ['Valor Total Gasto:', f'R$ {valor_total_gasto:,.2f}'],
            ['Valor Total Comprometido:', f'R$ {valor_total_comprometido:,.2f}'],
            ['Evolução Média das Obras:', f'{evolucao_media:.1f}%']
        ]
        
        resumo_table = Table(resumo_data, colWidths=[3*inch, 2.5*inch])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(resumo_table)
        story.append(Spacer(1, 30))
        
        # Lista detalhada de obras
        story.append(Paragraph("LISTAGEM DETALHADA DE OBRAS", heading_style))
        
        if works:
            # Cabeçalho da tabela
            obras_data = [['Nº Projeto', 'Nome', 'Status', 'Responsável', 'Início', 'Evolução', 'Orçamento']]
            
            for work in works:
                ultimo_relatorio = RelatorioMensal.query.filter_by(obra_id=work.id).order_by(RelatorioMensal.data_relatorio.desc()).first()
                evolucao = f'{ultimo_relatorio.evolucao_obra_percent}%' if ultimo_relatorio and ultimo_relatorio.evolucao_obra_percent else 'N/I'
                
                obras_data.append([
                    work.numero_projeto[:15] + '...' if work.numero_projeto and len(work.numero_projeto) > 15 else work.numero_projeto or 'N/I',
                    work.nome[:25] + '...' if len(work.nome) > 25 else work.nome,
                    work.status[:12] + '...' if len(work.status) > 12 else work.status,
                    work.responsavel.nome[:15] + '...' if len(work.responsavel.nome) > 15 else work.responsavel.nome,
                    work.data_inicio.strftime('%d/%m/%Y'),
                    evolucao,
                    f'R$ {work.orcamento:,.0f}' if work.orcamento else 'N/I'
                ])
            
            obras_table = Table(obras_data, colWidths=[1*inch, 1.8*inch, 1*inch, 1.2*inch, 0.8*inch, 0.7*inch, 1*inch])
            obras_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(obras_table)
        else:
            story.append(Paragraph("Nenhuma obra cadastrada no sistema.", styles['Normal']))
        
        story.append(PageBreak())
        
        # Análise por responsável
        story.append(Paragraph("ANÁLISE POR RESPONSÁVEL", heading_style))
        
        responsaveis_stats = {}
        for work in works:
            resp_nome = work.responsavel.nome
            if resp_nome not in responsaveis_stats:
                responsaveis_stats[resp_nome] = {
                    'total_obras': 0,
                    'obras_concluidas': 0,
                    'valor_total': 0,
                    'valor_gasto': 0
                }
            
            responsaveis_stats[resp_nome]['total_obras'] += 1
            if work.status == 'Concluída':
                responsaveis_stats[resp_nome]['obras_concluidas'] += 1
            if work.orcamento:
                responsaveis_stats[resp_nome]['valor_total'] += work.orcamento
            
            ultimo_relatorio = RelatorioMensal.query.filter_by(obra_id=work.id).order_by(RelatorioMensal.data_relatorio.desc()).first()
            if ultimo_relatorio and ultimo_relatorio.valor_gasto:
                responsaveis_stats[resp_nome]['valor_gasto'] += ultimo_relatorio.valor_gasto
        
        if responsaveis_stats:
            resp_data = [['Responsável', 'Total Obras', 'Concluídas', 'Valor Orçado', 'Valor Gasto']]
            
            for nome, stats in responsaveis_stats.items():
                resp_data.append([
                    nome[:20] + '...' if len(nome) > 20 else nome,
                    str(stats['total_obras']),
                    str(stats['obras_concluidas']),
                    f'R$ {stats["valor_total"]:,.0f}',
                    f'R$ {stats["valor_gasto"]:,.0f}'
                ])
            
            resp_table = Table(resp_data, colWidths=[2*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch])
            resp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgreen])
            ]))
            
            story.append(resp_table)
        
        story.append(Spacer(1, 30))
        
        # Rodapé
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.grey
        )
        
        story.append(Spacer(1, 50))
        story.append(Paragraph("Relatório gerado automaticamente pelo Sistema de Acompanhamento de Obras", footer_style))
        story.append(Paragraph(f"Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
        
        # Construir o PDF
        doc.build(story)
        
        # Preparar o buffer para envio
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'relatorio_geral_obras_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota de status da API
@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'online',
        'message': 'API do Sistema de Acompanhamento de Obras funcionando',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0'
    })

# Rota para servir arquivos estáticos
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# Rota para servir o frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado com sucesso!")
    
    print("Iniciando servidor Flask...")
    print("Sistema disponível em: http://localhost:5000")
    print("API disponível em: http://localhost:5000/api/status")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
