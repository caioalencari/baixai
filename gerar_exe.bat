@echo off
cd /d "%~dp0"

for %%A in (baixai.py baixai_nucleo.py yt-dlp.exe ffmpeg.exe ffprobe.exe LICENSE-ffmpeg.txt) do (
  if not exist "%%A" (
    echo Falta o arquivo %%A nesta pasta.
    pause
    exit /b
  )
)

echo Instalando o PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo.
  echo Nao consegui usar o Python. Confira se ele esta instalado com "Add python.exe to PATH" marcado.
  pause
  exit /b
)

echo.
echo Gerando o Baixai, isso leva alguns minutos...
set ICONE=
if exist "baixai.ico" set ICONE=--icon baixai.ico
python -m PyInstaller --noconfirm --clean --noconsole --onedir --name Baixai %ICONE% baixai.py
if not exist "dist\Baixai\Baixai.exe" (
  echo.
  echo Algo deu errado ao gerar o programa. Veja as mensagens acima.
  pause
  exit /b
)

copy /y "yt-dlp.exe" "dist\Baixai\" >nul
copy /y "ffmpeg.exe" "dist\Baixai\" >nul
copy /y "ffprobe.exe" "dist\Baixai\" >nul
if exist "deno.exe" copy /y "deno.exe" "dist\Baixai\" >nul
if exist "LICENSE-ffmpeg.txt" copy /y "LICENSE-ffmpeg.txt" "dist\Baixai\" >nul
if exist "LICENSE" copy /y "LICENSE" "dist\Baixai\LICENSE-Baixai.txt" >nul

echo.
echo Compactando...
if exist "Baixai.zip" del "Baixai.zip"
powershell -NoProfile -Command "Compress-Archive -Path 'dist\Baixai' -DestinationPath 'Baixai.zip'"

echo.
echo Pronto! Envie o arquivo Baixai.zip.
echo.
echo Codigo de verificacao (mande junto para a pessoa conferir que o arquivo nao foi alterado):
certutil -hashfile "Baixai.zip" SHA256 | findstr /v "hash CertUtil"
echo.
pause
