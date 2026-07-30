# 🚀 Guia de Instalação Rápida - Sistema de Acompanhamento de Obras v3.0

## Pré-requisitos
- Python 3.7 ou superior instalado
- pip (gerenciador de pacotes Python)

## Instalação em 5 Passos

### 1. Extrair o arquivo
```bash
unzip sistema-obras.zip
cd sistema-obras
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Executar o sistema
```bash
python app.py
```

### 4. Acessar no navegador
Abra: `http://localhost:5000`

### 5. Começar a usar!
- Dashboard com 8 métricas avançadas
- Cadastrar responsáveis e obras
- **Criar relatórios mensais** (nova funcionalidade)
- Gerar relatórios PDF profissionais

## ⚡ Comandos Rápidos

**Windows:**
```cmd
unzip sistema-obras.zip && cd sistema-obras && pip install -r requirements.txt && python app.py
```

**Linux/Mac:**
```bash
unzip sistema-obras.zip && cd sistema-obras && pip install -r requirements.txt && python app.py
```

## 🆕 Novas Funcionalidades v3.0

### **Sistema de Relatórios Mensais**
- **Baseado no documento oficial** de relatórios mensais
- Campos específicos: valor gasto, valor comprometido, evolução %
- Datas de seguro (início e vencimento)
- Comentários para serviços realizados
- Relatos da liderança para visitas e vistorias
- Suporte a fotos via URLs

### **Dashboard Avançado**
- 8 métricas principais incluindo evolução média
- Valor total gasto e comprometido
- Análise financeira em tempo real

### **Relatórios PDF Profissionais**
- Histórico de relatórios mensais por obra
- Análise de cronograma e atrasos
- Informações de seguro detalhadas
- Design corporativo profissional

## 🔧 Solução de Problemas

**Erro de porta em uso:**
```bash
# Mude a porta no arquivo app.py (linha final):
app.run(host='0.0.0.0', port=5001, debug=True)
```

**Erro de dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Banco de dados desatualizado:**
```bash
# O sistema irá atualizar automaticamente na primeira execução
# Se houver problemas, delete o arquivo obras.db e execute novamente
rm obras.db
python app.py
```

## 📱 Funcionalidades Principais

### **Gestão Completa**
- ✅ Dashboard executivo com 8 métricas
- ✅ Cadastro de obras com número de projeto
- ✅ Gestão de responsáveis (supervisores)
- ✅ **Sistema completo de relatórios mensais**

### **Relatórios Mensais** (Novo)
- ✅ Formulário baseado no documento oficial
- ✅ Campos obrigatórios: data, valores, evolução
- ✅ Informações de seguro
- ✅ Comentários detalhados
- ✅ Status de aprovação
- ✅ Filtros por obra e período

### **Relatórios PDF Avançados**
- ✅ Relatório geral com análise por responsável
- ✅ Relatório individual com histórico mensal
- ✅ Análise financeira e de cronograma
- ✅ Design profissional corporativo

### **Interface Moderna**
- ✅ 5 seções principais de navegação
- ✅ Design responsivo para todos os dispositivos
- ✅ Filtros dinâmicos e validações
- ✅ Notificações em tempo real

---

## 📋 Fluxo de Trabalho Recomendado

1. **Cadastrar Responsáveis** - Supervisores das obras
2. **Cadastrar Obras** - Com número de projeto e datas
3. **Criar Relatórios Mensais** - Até o dia 10 de cada mês
4. **Gerar Relatórios PDF** - Para análise e apresentação
5. **Acompanhar Dashboard** - Métricas em tempo real

**Sistema pronto para uso profissional!** 🎉
