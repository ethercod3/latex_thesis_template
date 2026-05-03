@echo off
setlocal EnableExtensions

cd /d "%~dp0.."

call :run_profile docx docx_pdf
if errorlevel 1 exit /b %errorlevel%

call :run_profile mermaid mermaid_diagrams
if errorlevel 1 exit /b %errorlevel%

call :run_profile python python_diagrams
if errorlevel 1 exit /b %errorlevel%

call :run_profile latex latex
if errorlevel 1 exit /b %errorlevel%

exit /b 0

:run_profile
echo.
echo ==^> %~1
docker compose --profile %~1 run --rm --build %~2
if errorlevel 1 exit /b %errorlevel%
exit /b 0
