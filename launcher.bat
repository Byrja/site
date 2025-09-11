@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Финансовый Telegram Бот - Лаунчер

:menu
cls
echo ================================
echo    Финансовый Telegram Бот
echo         Лаунчер v1.0
echo ================================
echo.
echo 1. Запустить бота
echo 2. Остановить бота
echo 3. Перезапустить бота
echo 4. Обновить бота из GitHub
echo 5. Проверить логи
echo 6. Установить/обновить зависимости
echo 7. Проверить конфигурацию
echo 8. Выход
echo.
echo ================================
set /p choice="Выберите действие (1-8): "

if "%choice%"=="1" goto start_bot
if "%choice%"=="2" goto stop_bot
if "%choice%"=="3" goto restart_bot
if "%choice%"=="4" goto update_bot
if "%choice%"=="5" goto check_logs
if "%choice%"=="6" goto install_deps
if "%choice%"=="7" goto check_config
if "%choice%"=="8" goto exit
goto menu

:start_bot
cls
echo Запуск бота...
echo.
echo Проверка зависимостей...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости!
    echo Попробуйте выбрать пункт 6 для ручной установки.
    echo.
)
python bot.py
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Не удалось запустить бота!
    echo Проверьте:
    echo 1. Установлен ли Python
    echo 2. Установлены ли зависимости (выберите пункт 6)
    echo 3. Правильно ли заполнен файл .env (пункт 7)
    echo.
    pause
)
goto menu

:stop_bot
cls
echo Остановка бота...
echo.
taskkill /f /im python.exe /fi "WINDOWTITLE eq Финансовый Telegram Бот*"
echo Бот остановлен.
echo.
pause
goto menu

:restart_bot
cls
echo Перезапуск бота...
echo.
taskkill /f /im python.exe /fi "WINDOWTITLE eq Финансовый Telegram Бот*"
timeout /t 2 /nobreak >nul
echo Проверка зависимостей...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости!
    echo Попробуйте выбрать пункт 6 для ручной установки.
    echo.
)
python bot.py
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Не удалось запустить бота!
    echo Проверьте:
    echo 1. Установлен ли Python
    echo 2. Установлены ли зависимости (выберите пункт 6)
    echo 3. Правильно ли заполнен файл .env (пункт 7)
    echo.
    pause
)
goto menu

:update_bot
cls
echo Обновление бота из GitHub...
echo.
git pull
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Не удалось обновить бота!
    echo Проверьте подключение к интернету и настройки Git.
    echo.
    pause
) else (
    echo.
    echo Бот успешно обновлен!
    echo Установка обновленных зависимостей...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo ОШИБКА: Не удалось установить зависимости!
        echo Попробуйте выбрать пункт 6 для ручной установки.
        echo.
        pause
    ) else (
        echo Зависимости успешно установлены!
        echo.
        pause
    )
)
goto menu

:check_logs
cls
echo Проверка логов...
echo.
if exist bot.log (
    type bot.log
) else (
    echo Файл логов не найден.
)
echo.
pause
goto menu

:install_deps
cls
echo Установка/обновление зависимостей...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Не удалось установить зависимости!
    echo Проверьте:
    echo 1. Установлен ли Python и pip
    echo 2. Подключение к интернету
    echo.
    pause
) else (
    echo.
    echo Зависимости успешно установлены/обновлены!
    echo.
    pause
)
goto menu

:check_config
cls
echo Проверка конфигурации...
echo.
python check_config.py
echo.
pause
goto menu

:exit
cls
echo Спасибо за использование лаунчера!
echo.
pause
exit