@echo off
REM Define o título da janela do console
TITLE Iniciador da Aplicacao - Bom Chefe

REM Navega para o diretório onde o script está localizado
cd /d "%~dp0"

echo.
echo =========================================
echo  INICIANDO APLICACAO BOM CHEFE...
echo =========================================
echo.
echo Por favor, aguarde enquanto os servicos sao iniciados.
echo Isso pode levar um minuto na primeira vez.
echo.

REM Inicia os containers em modo "detached" (em segundo plano)
docker-compose up -d

echo.
echo =================================================================
echo  APLICACAO INICIADA COM SUCESSO!
echo.
echo  - Para acessar o sistema, abra o navegador em: http://localhost
echo  - Para parar a aplicacao, execute o arquivo "parar.bat".
echo =================================================================
echo.

REM Mantém a janela aberta para o usuário ler a mensagem
pause
