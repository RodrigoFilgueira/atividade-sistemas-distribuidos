@echo off
title MiniAWS - Simulador de Serviços AWS
echo ==========================================================
echo               MiniAWS - Simulador de Serviços AWS
echo ==========================================================
echo.
echo [1/2] Verificando e instalando dependencias (Flask)...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao instalar dependencias com pip. Certifique-se de ter o Python 3 instalado e no PATH.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo [2/2] Iniciando o servidor Flask em http://localhost:5000/ ...
python app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERRO] O servidor Flask terminou com erro.
    pause
)
