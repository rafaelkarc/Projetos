# Sistema de Acompanhamento de Obras

Um sistema completo para acompanhamento de obras com relatórios mensais, desenvolvido com Flask (backend) e HTML/CSS/JavaScript (frontend), baseado na estrutura de relatórios mensais profissionais.

## 📋 Funcionalidades

### Dashboard Executivo
- Visão geral com estatísticas avançadas das obras
- Contadores de obras por status
- Valor total dos orçamentos, gastos e comprometidos
- Evolução média das obras em percentual
- Indicadores de obras atrasadas
- Ações rápidas para navegação

### Gerenciamento de Obras
- ✅ Cadastro completo de obras com número de projeto
- ✅ Campos específicos: data início real da construção, data de término e dedicação
- ✅ Edição e exclusão de obras
- ✅ Filtros por status e responsável
- ✅ Status: Em Planejamento, Em Andamento, Pausada, Concluída
- ✅ Visualização da evolução atual baseada no último relatório mensal

### Gerenciamento de Responsáveis
- ✅ Cadastro de pessoas responsáveis (supervisores)
- ✅ Campos: nome, função, contato, email, CPF
- ✅ Edição e exclusão de responsáveis
- ✅ Validação de CPF com máscara automática

### **Relatórios Mensais** (Nova Funcionalidade)
- ✅ **Sistema de relatórios mensais baseado no documento oficial**
- ✅ **Campos obrigatórios do sistema:**
  - Data do Relatório (último dia útil do mês)
  - Valor Gasto e Valor Comprometido
  - Evolução da Obra em percentual
  - Data do Início e Vencimento do Seguro
- ✅ **Comentários detalhados:**
  - Serviços realizados no período
  - Relatos da liderança (visitas e vistorias)
- ✅ **Suporte a fotos:** URLs para Foto 1 e Foto 2
- ✅ **Filtros por obra e período (mês/ano)**
- ✅ **Status de aprovação dos relatórios**

### Relatórios PDF Avançados
- ✅ **Relatório geral** com análise por responsável
- ✅ **Relatório individual por obra** com histórico de relatórios mensais
- ✅ **Análise de cronograma e atrasos**
- ✅ **Informações financeiras detalhadas**
- ✅ **Evolução física das obras**

## 🚀 Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Extrair o arquivo ZIP**
   ```bash
   unzip sistema-obras.zip
   cd sistema-obras
   ```

2. **Criar ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar o sistema**
   ```bash
   python app.py
   ```

5. **Acessar o sistema**
   - Abra o navegador e vá para: `http://localhost:5000`
   - A API estará disponível em: `http://localhost:5000/api/status`

## 🏗️ Estrutura do Projeto

```
sistema-obras/
├── app.py              # Backend Flask com API REST completa
├── index.html          # Interface do usuário moderna
├── style.css           # Estilos e design responsivo
├── script.js           # Lógica frontend e interações
├── requirements.txt    # Dependências Python
├── README.md          # Esta documentação
├── INSTALACAO.md      # Guia de instalação rápida
└── obras.db           # Banco de dados SQLite (criado automaticamente)
```

## 🎨 Interface

### Design Profissional
- Interface responsiva baseada em sistemas corporativos
- Sidebar de navegação com 5 seções principais
- Cards estatísticos no dashboard com 8 métricas
- Modais para formulários com validação
- Tabelas com ações inline e filtros
- Notificações em tempo real

### Recursos de UX
- Indicador de status da API em tempo real
- Loading overlay durante operações
- Confirmações para exclusões
- Validação de formulários em tempo real
- Atalhos de teclado (Ctrl+N, ESC)
- Filtros dinâmicos por obra e período

## 📊 API REST Completa

### Endpoints Principais

#### Dashboard
- `GET /api/dashboard` - Estatísticas gerais avançadas

#### Responsáveis
- `GET /api/responsibles` - Listar todos
- `POST /api/responsibles` - Criar novo
- `GET /api/responsibles/{id}` - Obter por ID
- `PUT /api/responsibles/{id}` - Atualizar
- `DELETE /api/responsibles/{id}` - Excluir

#### Obras
- `GET /api/works` - Listar todas (com filtros)
- `POST /api/works` - Criar nova
- `GET /api/works/{id}` - Obter por ID
- `PUT /api/works/{id}` - Atualizar
- `DELETE /api/works/{id}` - Excluir

#### **Relatórios Mensais** (Novos Endpoints)
- `GET /api/works/{obra_id}/reports` - Listar relatórios de uma obra
- `POST /api/works/{obra_id}/reports` - Criar novo relatório mensal
- `PUT /api/reports/{id}` - Atualizar relatório mensal
- `DELETE /api/reports/{id}` - Excluir relatório mensal

#### Relatórios PDF
- `GET /api/reports/general` - Relatório geral (PDF)
- `GET /api/reports/works/{id}` - Relatório de obra específica (PDF)

## 🗄️ Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### pessoa_responsavel
- `id` (INTEGER, PK)
- `nome` (VARCHAR(100), NOT NULL)
- `contato` (VARCHAR(100))
- `funcao` (VARCHAR(100))
- `email` (VARCHAR(120))
- `cpf` (VARCHAR(14))
- `data_cadastro` (DATETIME)

### obra
- `id` (INTEGER, PK)
- `numero_projeto` (VARCHAR(50)) **[NOVO]**
- `nome` (VARCHAR(200), NOT NULL)
- `descricao` (TEXT)
- `endereco` (VARCHAR(300))
- `data_inicio` (DATE, NOT NULL)
- `data_inicio_real` (DATE) **[NOVO]**
- `data_fim` (DATE)
- `data_prevista_fim` (DATE)
- `data_termino_dedicacao` (DATE) **[NOVO]**
- `orcamento` (FLOAT)
- `status` (VARCHAR(50))
- `responsavel_id` (INTEGER, FK)
- `data_cadastro` (DATETIME)

### **relatorio_mensal** (Nova Tabela)
- `id` (INTEGER, PK)
- `obra_id` (INTEGER, FK)
- `data_relatorio` (DATE, NOT NULL)
- `valor_gasto` (FLOAT)
- `valor_comprometido` (FLOAT)
- `data_inicio_seguro` (DATE)
- `data_vencimento_seguro` (DATE)
- `evolucao_obra_percent` (FLOAT)
- `comentarios` (TEXT)
- `relatos_lideranca` (TEXT)
- `foto1_url` (VARCHAR(255))
- `foto2_url` (VARCHAR(255))
- `data_criacao` (DATETIME)
- `aprovado` (BOOLEAN)

## 🔧 Desenvolvimento

### Tecnologias Utilizadas

**Backend:**
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-CORS 4.0.0
- ReportLab 4.0.4

**Frontend:**
- HTML5 semântico
- CSS3 com Flexbox/Grid
- JavaScript ES6+
- Font Awesome 6.0 (ícones)

### Recursos Implementados

**Backend:**
- API RESTful completa com 15+ endpoints
- Sistema de relatórios mensais
- Validação de dados avançada
- Tratamento de erros robusto
- CORS configurado
- Geração de PDF com análise financeira
- Relacionamentos complexos entre tabelas

**Frontend:**
- SPA (Single Page Application) com 5 seções
- Design responsivo profissional
- Sistema de relatórios mensais interativo
- Componentes modais avançados
- Notificações toast personalizadas
- Loading states e validações
- Máscaras de entrada (CPF)
- Filtros dinâmicos por período

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:
- 💻 Desktop (1200px+)
- 📱 Tablet (768px - 1199px)
- 📱 Mobile (até 767px)

## 🎯 Melhorias Baseadas no Documento

Baseado no documento "Apresentação-Relatórios-Mensais_rev1.pptx", foram implementadas:

### **1. Sistema de Relatórios Mensais Completo**
- Campos exatos do documento: valor gasto, valor comprometido, evolução %
- Datas de seguro (início e vencimento)
- Data início real da construção
- Data de término e dedicação
- Comentários para serviços realizados
- Relatos da liderança para visitas e vistorias

### **2. Interface Profissional**
- Dashboard com 8 métricas principais
- Seção dedicada aos relatórios mensais
- Filtros por obra e período (mês/ano)
- Modais maiores para formulários complexos
- Status de aprovação dos relatórios

### **3. Funcionalidades Avançadas**
- Número de projeto para identificação
- Evolução da obra em tempo real no dashboard
- Análise financeira detalhada nos relatórios PDF
- Histórico completo de relatórios mensais
- Suporte a fotos via URLs

### **4. Relatórios PDF Profissionais**
- Relatório geral com análise por responsável
- Histórico de relatórios mensais por obra
- Análise de cronograma e atrasos
- Informações de seguro e evolução física
- Design corporativo profissional

## 🐛 Solução de Problemas

### Erro de Porta em Uso
```bash
# Verificar processo usando a porta 5000
lsof -i :5000

# Matar processo se necessário
kill -9 <PID>
```

### Erro de Dependências
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Banco de Dados Corrompido
```bash
# Deletar banco existente (perderá dados)
rm obras.db

# Reiniciar aplicação para recriar
python app.py
```

## 📄 Licença

Este projeto foi desenvolvido como um sistema profissional de acompanhamento de obras e pode ser usado livremente para fins educacionais e comerciais.

## 👨‍💻 Desenvolvedor

Sistema desenvolvido com foco em:
- Arquitetura baseada em documentação oficial
- Implementação fiel aos requisitos do documento
- Interface moderna e intuitiva
- Funcionalidades completas de relatórios mensais
- Análise financeira e de cronograma avançada

---

**Versão:** 3.0 - Relatórios Mensais  
**Data:** Setembro 2025  
**Baseado em:** Apresentação-Relatórios-Mensais_rev1.pptx
