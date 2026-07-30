@echo off
REM Visualizador do Banco de Dados - Inicializador para Windows
REM Duplo clique para executar

setlocal enabledelayedexpansion

REM Obter diretório do script
set SCRIPT_DIR=%~dp0

REM Mudar para o diretório do script
cd /d "%SCRIPT_DIR%"

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERRO: Python não está instalado!
    echo ========================================
    echo.
    echo Este programa requer Python 3.8 ou superior.
    echo.
    echo Baixe Python em: https://www.python.org/downloads/
    echo.
    echo Certifique-se de marcar "Add Python to PATH" durante a instalação.
    echo.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Instalando dependências...
    echo ========================================
    echo.
    python -m pip install flask flask-cors openpyxl requests -q
    if %errorlevel% neq 0 (
        echo.
        echo ERRO ao instalar dependências!
        pause
        exit /b 1
    )
)

REM Iniciar a aplicação
echo.
echo ========================================
echo Iniciando Visualizador do Banco de Dados
echo ========================================
echo.
echo Aguarde... abrindo navegador em 2 segundos
echo.

python app.py

pause
