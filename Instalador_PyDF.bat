@echo off
setlocal EnableDelayedExpansion
title GERENCIADOR MESTRE PYDF - V4 (NETWORK PRO)
color 0B
chcp 65001 >nul
mode con: cols=120 lines=40

:: --- DEFINICOES GLOBAIS ---
cd /d "%~dp0"
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "SENDTO_DIR=%APPDATA%\Microsoft\Windows\SendTo"

:MENU_PRINCIPAL
cls
echo ==============================================================================
echo   GERENCIADOR MESTRE PYDF - V4 (COMPATIVEL COM REDE MULTI-USUARIO)
echo ==============================================================================
echo.
echo   [1] INSTALAR / ATUALIZAR (Gera executaveis que funcionam em qualquer PC)
echo   [2] FERRAMENTAS DE DEBUG
echo   [3] RESET
echo   [4] TESTE DE SISTEMA
echo.
echo ==============================================================================
set /p "OPCAO=Escolha uma opcao: "

if "%OPCAO%"=="1" goto INSTALACAO_COMPLETA
if "%OPCAO%"=="2" goto MENU_DEBUG
if "%OPCAO%"=="3" goto MENU_RESET
if "%OPCAO%"=="4" goto RODAR_TESTES

goto MENU_PRINCIPAL

:: ==============================================================================
:: [1] INSTALACAO BLINDADA
:: ==============================================================================
:INSTALACAO_COMPLETA
cls
echo [STATUS] Iniciando Instalacao Hibrida...
echo.

:: 1. Verificacao de Dependencias (Apenas visual, o wrapper vai decidir na hora)
if exist "%SCRIPT_DIR%\python_mini\python.exe" (
    echo [OK] Pasta 'python_mini' detectada (Modo Portatil Ativo).
    "%SCRIPT_DIR%\python_mini\python.exe" -m pip install --upgrade pikepdf pypdf pymupdf >nul 2>&1
) else (
    echo [INFO] Pasta 'python_mini' nao encontrada. Usaremos o Python do Sistema.
    python -m pip install --upgrade pikepdf pypdf pymupdf >nul 2>&1
)

:: 2. Gera Wrappers DINAMICOS (O segredo esta aqui)
echo.
echo [STATUS] Criando executaveis universais...

call :GerarWrapperDinamico "_run_fatiar.bat" "dividir.py"
call :GerarWrapperDinamico "_run_juntar.bat" "juntar.py"
call :GerarWrapperDinamico "_run_juntar_turbo.bat" "juntar_turbo.py"
call :GerarWrapperDinamico "_run_smart.bat" "dividir_smart.py"
call :GerarWrapperDinamico "_run_renomear.bat" "renomear.py"

echo [OK] Wrappers gerados.

:: 3. Cria Atalhos Locais (Isso cada usuario precisa fazer 1 vez)
echo.
echo [STATUS] Criando atalhos no SEU computador...
:: Para o atalho, precisamos apontar para um executavel. 
:: Usamos o CMD.exe para chamar o .bat, assim o atalho fica generico.
call :CriarAtalhoGenerico "DIVIDIR (PyDF).lnk" "_run_fatiar.bat"
call :CriarAtalhoGenerico "JUNTAR (PyDF).lnk" "_run_juntar.bat"
call :CriarAtalhoGenerico "JUNTAR TURBO (PyDF).lnk" "_run_juntar_turbo.bat"
call :CriarAtalhoGenerico "DIVIDIR SMART (PyDF).lnk" "_run_smart.bat"
call :CriarAtalhoGenerico "RENOMEAR (PyDF).lnk" "_run_renomear.bat"

echo [OK] Atalhos criados!

echo.
echo ==============================================================================
echo   INSTALACAO UNIVERSAL CONCLUIDA!
echo   Agora os scripts funcionam tanto no seu PC quanto na rede.
echo ==============================================================================
pause
goto MENU_PRINCIPAL

:: ==============================================================================
:: [2] MENU DEBUG
:: ==============================================================================
:MENU_DEBUG
cls
echo [A] SIMULADOR "SEND TO"
echo [B] LIMPAR CACHE
echo [V] VOLTAR
set /p "DEBUG_OPT=Escolha: "

if /i "%DEBUG_OPT%"=="A" goto SIMULADOR
if /i "%DEBUG_OPT%"=="B" goto LIMPAR_CACHE
if /i "%DEBUG_OPT%"=="V" goto MENU_PRINCIPAL
goto MENU_DEBUG

:SIMULADOR
cls
echo Arraste o PDF para testar o wrapper dinamico:
set /p "SCRIPT_TESTE=Nome do script (ex: renomear.py): "
set /p "ARQUIVO_TESTE=Arquivo PDF: "
set "ARQUIVO_TESTE=%ARQUIVO_TESTE:"=%"
cls
if exist "%SCRIPT_DIR%\python_mini\python.exe" (
    "%SCRIPT_DIR%\python_mini\python.exe" "%SCRIPT_TESTE%" "%ARQUIVO_TESTE%"
) else (
    python "%SCRIPT_TESTE%" "%ARQUIVO_TESTE%"
)
pause
goto MENU_DEBUG

:LIMPAR_CACHE
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo [OK] Limpo.
timeout /t 2 >nul
goto MENU_DEBUG

:: ==============================================================================
:: [3] RESET
:: ==============================================================================
:MENU_RESET
del /f /q "%SENDTO_DIR%\*PyDF*.lnk" >nul 2>&1
del /f /q "%SCRIPT_DIR%\_run_*.bat" >nul 2>&1
echo [OK] Resetado.
pause
goto MENU_PRINCIPAL

:: ==============================================================================
:: [4] TESTES
:: ==============================================================================
:RODAR_TESTES
cls
if exist "teste_sistema.py" (
    if exist "%SCRIPT_DIR%\python_mini\python.exe" (
        "%SCRIPT_DIR%\python_mini\python.exe" "teste_sistema.py"
    ) else (
        python "teste_sistema.py"
    )
) else (
    echo [ERRO] teste_sistema.py faltando.
)
pause
goto MENU_PRINCIPAL


:: ==============================================================================
:: FUNCOES ESPECIAIS (A MAGICA ACONTECE AQUI)
:: ==============================================================================

:GerarWrapperDinamico
set "NOME_BAT=%~1"
set "SCRIPT_PY=%~2"

(
echo @echo off
echo chcp 65001 ^>nul
echo pushd "%%~dp0"
echo.
echo :: --- DETECCAO AUTOMATICA DE MOTOR ---
echo if exist "%%~dp0python_mini\python.exe" ^(
echo     set "MOTOR=%%~dp0python_mini\python.exe"
echo ^) else ^(
echo     set "MOTOR=python"
echo ^)
echo.
echo :: --- EXECUCAO ---
echo "%%MOTOR%%" "%%~dp0%SCRIPT_PY%" %%*
echo.
echo if %%errorlevel%% NEQ 0 ^(
echo     echo [ERRO] O script falhou ou o Python nao foi encontrado.
echo     pause
echo ^)
echo popd
) > "%NOME_BAT%"
goto :eof

:CriarAtalhoGenerico
set "NOME_LNK=%~1"
set "NOME_BAT=%~2"
set "DESTINO_LNK=%SENDTO_DIR%\%NOME_LNK%"
set "CAMINHO_BAT=%SCRIPT_DIR%\%NOME_BAT%"

:: Aqui usamos o cmd.exe /c para executar o .bat. 
:: Isso garante que o atalho funcione mesmo se o drive de rede mudar a letra.
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESTINO_LNK%'); $s.TargetPath = 'cmd.exe'; $s.Arguments = '/c \"\"%CAMINHO_BAT%\"\"'; $s.IconLocation = 'shell32.dll,265'; $s.Save()"
goto :eof