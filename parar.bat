@echo off
REM Define o título da janela do console
TITLE Finalizador da Aplicacao - Bom Chefe

REM Navega para o diretório onde o script está localizado
cd /d "%~dp0"

echo.
echo =========================================
echo  PARANDO APLICACAO BOM CHEFE...
echo =========================================
echo.
echo Por favor, aguarde enquanto os containers sao parados e removidos.
echo.

REM Para e remove os containers, redes e volumes definidos no compose
docker-compose down

echo.
echo =========================================
echo  APLICACAO PARADA COM SUCESSO!
echo =========================================
echo.

REM Mantém a janela aberta para o usuário ler a mensagem
pause
