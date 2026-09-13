@echo off
chcp 65001 >nul
title Hand Tracking - Tahap 1

echo ================================================
echo   HAND TRACKING PROJECT - Tahap 1
echo ================================================
echo.

:: Pindah ke folder script ini berada
cd /d "%~dp0"

:: Cari Python 3.11
set PYTHON=C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON%" (
    echo [ERROR] Python 3.11 tidak ditemukan di:
    echo         %PYTHON%
    echo.
    echo Coba gunakan perintah: python main.py
    pause
    exit /b 1
)

echo [OK] Python ditemukan: %PYTHON%
echo [OK] Menjalankan Hand Tracking...
echo.

"%PYTHON%" main.py

echo.
echo Program selesai.
pause
