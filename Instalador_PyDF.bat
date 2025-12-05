@echo off
setlocal EnableDelayedExpansion
title INSTALADOR PYDF - PEDRO TAVARES
color 0A
chcp 65001 >nul

:: --- DEFINICOES GLOBAIS ---
cd /d "%~dp0"
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "SENDTO_DIR=%APPDATA%\Microsoft\Windows\SendTo"

:MENU
cls
echo ========================================================
echo   INSTALADOR E GERENCIADOR PYDF - POR PEDRO TAVARES
echo ========================================================
echo.
echo    [1] HARD RESET (Apagar TUDO: Libs, Atalhos, Wrappers)
echo    [2] SOFT RESET (Atualizar/Limpar apenas Atalhos)
echo    [3] INSTALAR / REPARAR (Verificar ambiente e libs)
echo    [4] TESTE DE SISTEMA (Rodar suite de testes)
echo.
echo ========================================================
set /p "OPCAO=Escolha uma opcao (1-4): "

if "%OPCAO%"=="1" goto OPCAO_RESET_TOTAL
if "%OPCAO%"=="2" goto OPCAO_RESET_SOFT
if "%OPCAO%"=="3" goto OPCAO_DIAGNOSTICO
if "%OPCAO%"=="4" goto OPCAO_TESTES

echo Opcao invalida.
timeout /t 2 >nul
goto MENU

:: ========================================================
::                OPCAO 1: HARD RESET
:: ========================================================
:OPCAO_RESET_TOTAL
cls
echo [!] INICIANDO HARD RESET...
echo.

:: 1. Remove Libs (Logica linear para evitar erro com parenteses em x86)
call :LocalizarPythonSilencioso
if not defined PYTHON_REAL goto :SKIP_LIB_UNINSTALL

echo [1/3] Removendo bibliotecas (pypdf, pikepdf, pymupdf)...
"%PYTHON_REAL%" -m pip uninstall -y pypdf pikepdf pymupdf >nul 2>&1
echo        [OK] Bibliotecas limpas.
goto :END_LIB_CHECK

:SKIP_LIB_UNINSTALL
echo [1/3] Python nao encontrado, pulando remocao de lib.

:END_LIB_CHECK
:: 2. Remove Atalhos
echo [2/3] Excluindo atalhos antigos...
del /f /q "%SENDTO_DIR%\*Fatiar*.lnk" >nul 2>&1
del /f /q "%SENDTO_DIR%\*Juntar*.lnk" >nul 2>&1
del /f /q "%SENDTO_DIR%\*Smart*.lnk" >nul 2>&1
del /f /q "%SENDTO_DIR%\*Renomear*.lnk" >nul 2>&1
echo        [OK] Atalhos removidos.

:: 3. Remove Wrappers
echo [3/3] Limpando arquivos temporarios (.bat)...
del /f /q "%SCRIPT_DIR%\_run_*.bat" >nul 2>&1
echo        [OK] Wrappers deletados.

echo.
echo ========================================================
echo        HARD RESET CONCLUIDO.
echo ========================================================
pause
goto MENU

:: ========================================================
::                OPCAO 2: SOFT RESET
:: ========================================================
:OPCAO_RESET_SOFT
cls
echo [!] INICIANDO SOFT RESET (Foco em Atalhos)...
echo.

:: 1. Apenas limpa os atalhos para recriar depois limpo
echo [1/2] Removendo atalhos do menu de contexto...
del /f /q "%SENDTO_DIR%\*Fatiar*.lnk" >nul 2>&1
del /f /q "%SENDTO_DIR%\*Juntar*.lnk" >nul 2>&1
del /f /q "%SENDTO_DIR%\*Smart*.lnk" >nul 2>&1
del /f /q "%SENDTO_DIR%\*Renomear*.lnk" >nul 2>&1
echo        [OK] Atalhos antigos removidos.

:: 2. Remove wrappers antigos para garantir versoes novas
echo [2/2] Atualizando scripts de lancamento...
del /f /q "%SCRIPT_DIR%\_run_*.bat" >nul 2>&1
echo        [OK] Limpeza concluida.

echo.
echo ========================================================
echo        SOFT RESET CONCLUIDO.
echo ========================================================
echo Dica: Agora use a Opcao 3 para reinstalar os atalhos.
pause
goto MENU

:: ========================================================
::            OPCAO 3: INSTALAR / REPARAR
:: ========================================================
:OPCAO_DIAGNOSTICO
cls
echo [?] INICIANDO DIAGNOSTICO E INSTALACAO...
echo.

:: --- CHECK 1: PYTHON ---
echo [1/5] Verificando Motor Python...
call :LocalizarPythonVerbose
if not defined PYTHON_REAL (
    echo [ERRO] Python nao encontrado.
    echo Buscando instalador automatico...
    call :InstalarPython
)
:: Verifica versão
for /f "tokens=*" %%v in ('"%PYTHON_REAL%" --version') do set "PY_VER=%%v"
echo        [STATUS] Versao detectada: %PY_VER%

:: --- CHECK 2: BIBLIOTECAS ---
echo.
echo [2/5] Verificando dependencias (pikepdf, pypdf, pymupdf)...
"%PYTHON_REAL%" -m pip install pikepdf pypdf pymupdf >nul 2>&1
echo        [OK] Bibliotecas instaladas/atualizadas.

:: --- CHECK 3: ARQUIVOS FONTE (.py) ---
echo.
echo [3/5] Validando integridade dos scripts...
set "FALTANDO=0"
if not exist "%SCRIPT_DIR%\dividir.py" (echo [X] Faltando dividir.py & set FALTANDO=1)
if not exist "%SCRIPT_DIR%\juntar.py" (echo [X] Faltando juntar.py & set FALTANDO=1)
if not exist "%SCRIPT_DIR%\dividir_smart.py" (echo [X] Faltando dividir_smart.py & set FALTANDO=1)
if not exist "%SCRIPT_DIR%\renomear.py" (echo [X] Faltando renomear.py & set FALTANDO=1)

if "%FALTANDO%"=="0" (
    echo        [OK] Scripts base encontrados.
) else (
    echo        [ALERTA] Arquivos faltando! O programa pode falhar.
)

:: --- CHECK 4: WRAPPERS (.bat locais) ---
echo.
echo [4/5] Gerando Executaveis Ocultos (Modo Rapido)...
(
echo @echo off
echo "%PYTHON_REAL%" "%%~dp0dividir.py" %%*
echo exit
) > "_run_fatiar.bat"

(
echo @echo off
echo "%PYTHON_REAL%" "%%~dp0juntar.py" %%*
echo exit
) > "_run_juntar.bat"

(
echo @echo off
echo "%PYTHON_REAL%" "%%~dp0dividir_smart.py" %%*
echo exit
) > "_run_smart.bat"

(
echo @echo off
echo "%PYTHON_REAL%" "%%~dp0renomear.py" %%*
echo exit
) > "_run_renomear.bat"
echo        [OK] Wrappers gerados.

:: --- CHECK 5: ATALHOS DE CONTEXTO ---
echo.
echo [5/5] Criando Atalhos no Menu de Contexto...
call :CriarAtalho "01 - DIVIDIR (PyDF).lnk" "_run_fatiar.bat"
call :CriarAtalho "02 - JUNTAR (PyDF).lnk" "_run_juntar.bat"
call :CriarAtalho "03 - DIVIDIR SMART (PyDF).lnk" "_run_smart.bat"
call :CriarAtalho "04 - RENOMEAR (PyDF).lnk" "_run_renomear.bat"
echo        [OK] Atalhos instalados com sucesso!

echo.
echo ========================================================
echo        INSTALACAO CONCLUIDA!
echo ========================================================
echo Agora voce pode clicar com o botao direito em qualquer PDF
echo e usar a opcao "Enviar Para".
echo.
pause
goto MENU

:: ========================================================
::                OPCAO 4: TESTE DE SISTEMA
:: ========================================================
:OPCAO_TESTES
cls
echo [DEBUG] Iniciando ambiente de teste...

call :LocalizarPythonVerbose
if not defined PYTHON_REAL (
    echo [ERRO FATAL] Python nao detectado para teste.
    pause
    goto MENU
)

echo.
echo [!] RODANDO TESTES...
echo -------------------------------------------------------
:: Verifica se o arquivo de teste existe antes de rodar
if exist "%SCRIPT_DIR%\teste_sistema.py" (
    "%PYTHON_REAL%" "%SCRIPT_DIR%\teste_sistema.py"
    if !errorlevel! NEQ 0 (
        echo.
        echo [FALHA] O teste encontrou erros. Verifique o log acima.
    ) else (
        echo.
        echo [SUCESSO] Todos os sistemas operacionais.
    )
) else (
    echo [ERRO] Arquivo 'teste_sistema.py' nao encontrado.
)

echo -------------------------------------------------------
pause
goto MENU


:: ========================================================
::                FUNCOES AUXILIARES
:: ========================================================

:LocalizarPythonSilencioso
set "PYTHON_REAL="
for /f "tokens=*" %%i in ('where python 2^>nul') do (
    echo "%%i" | find /i "WindowsApps" >nul
    if errorlevel 1 if not defined PYTHON_REAL set "PYTHON_REAL=%%i"
)
if not defined PYTHON_REAL if exist "%LocalAppData%\Python\bin\python.exe" set "PYTHON_REAL=%LocalAppData%\Python\bin\python.exe"
if not defined PYTHON_REAL for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYTHON_REAL=%%D\python.exe"
if not defined PYTHON_REAL for /d %%D in ("%ProgramFiles%\Python3*") do if exist "%%D\python.exe" set "PYTHON_REAL=%%D\python.exe"
goto :eof

:LocalizarPythonVerbose
call :LocalizarPythonSilencioso
if defined PYTHON_REAL echo        [OK] Motor: "%PYTHON_REAL%"
goto :eof

:InstalarPython
echo        [AVISO] Tentando instalador local...
if exist "python-*.exe" (
    for %%f in ("python-*.exe") do set "INSTALLER=%%f"
    "!INSTALLER!" /quiet PrependPath=1 Include_test=0
    timeout /t 10 >nul
    call :LocalizarPythonSilencioso
) else (
    echo        [ERRO] Instalador nao encontrado. Instale o Python manualmente.
    pause
    exit /b
)
goto :eof

:CriarAtalho
set "NOME_LNK=%~1"
set "NOME_BAT=%~2"
set "DESTINO_LNK=%SENDTO_DIR%\%NOME_LNK%"
set "CAMINHO_BAT=%SCRIPT_DIR%\%NOME_BAT%"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESTINO_LNK%'); $s.TargetPath = '%CAMINHO_BAT%'; $s.IconLocation = '%PYTHON_REAL%,0'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"
goto :eof