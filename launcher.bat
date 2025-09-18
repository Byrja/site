@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Финансовый Telegram Бот - Лаунчер

:menu
cls
echo ================================
echo    Финансовый Telegram Бот
echo         Лаунчер v1.1
echo ================================
echo.
echo 1. Запустить бота
echo 2. Остановить бота
echo 3. Перезапустить бота
echo 4. Обновить бота из GitHub
echo 5. Проверить логи
echo 6. Установить/обновить зависимости
echo 7. Проверить конфигурацию
echo 8. Диагностика проблем
echo 9. Помощь по устранению неполадок
echo 10. Выход
echo.
echo ================================
set /p choice="Выберите действие (1-10): "

if "%choice%"=="1" goto start_bot
if "%choice%"=="2" goto stop_bot
if "%choice%"=="3" goto restart_bot
if "%choice%"=="4" goto update_bot
if "%choice%"=="5" goto check_logs
if "%choice%"=="6" goto install_deps
if "%choice%"=="7" goto check_config
if "%choice%"=="8" goto diagnose_issues
if "%choice%"=="9" goto troubleshooting
if "%choice%"=="10" goto exit
goto menu

:start_bot
cls
echo Запуск бота...
echo.

REM Проверка наличия .env файла и токена
if not exist ".env" (
    echo ОШИБКА: Файл .env не найден!
    echo Создайте файл .env на основе .env.example и укажите токен бота
    echo.
    pause
    goto menu
)

REM Проверка наличия токена в .env файле
findstr /C:"TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env >nul
if %errorlevel% equ 0 (
    echo ОШИБКА: Токен бота не установлен в файле .env!
    echo Откройте файл .env и укажите правильный токен бота
    echo.
    pause
    goto menu
)

echo Проверка зависимостей...
python -m pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости!
    echo Попробуйте выбрать пункт 6 для ручной установки.
    echo.
)
echo Остановка предыдущих экземпляров бота...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Финансовый Telegram Бот*" >nul 2>&1
taskkill /f /im python.exe /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE ne Unknown Python Window" >nul 2>&1
wmic process where "name='python.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
powershell "Get-Process python | Where-Object {$_.MainWindowTitle -like '*Финансовый Telegram Бот*'} | Stop-Process -Force" >nul 2>&1
timeout /t 2 /nobreak >nul
start "Финансовый Telegram Бот" /min python bot.py
echo Бот запущен в фоновом режиме.
timeout /t 2 /nobreak >nul
goto menu

:stop_bot
cls
echo Остановка бота...
echo.
taskkill /f /im python.exe /fi "WINDOWTITLE eq Финансовый Telegram Бот*" >nul 2>&1
taskkill /f /im python.exe /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE ne Unknown Python Window" >nul 2>&1
wmic process where "name='python.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
powershell "Get-Process python | Where-Object {$_.MainWindowTitle -like '*Финансовый Telegram Бот*'} | Stop-Process -Force" >nul 2>&1
echo Бот остановлен.
echo.
pause
goto menu

:restart_bot
cls
echo Перезапуск бота...
echo.

REM Проверка наличия .env файла и токена
if not exist ".env" (
    echo ОШИБКА: Файл .env не найден!
    echo Создайте файл .env на основе .env.example и укажите токен бота
    echo.
    pause
    goto menu
)

REM Проверка наличия токена в .env файле
findstr /C:"TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env >nul
if %errorlevel% equ 0 (
    echo ОШИБКА: Токен бота не установлен в файле .env!
    echo Откройте файл .env и укажите правильный токен бота
    echo.
    pause
    goto menu
)

echo Остановка предыдущих экземпляров бота...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Финансовый Telegram Бот*" >nul 2>&1
taskkill /f /im python.exe /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE ne Unknown Python Window" >nul 2>&1
wmic process where "name='python.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
powershell "Get-Process python | Where-Object {$_.MainWindowTitle -like '*Финансовый Telegram Бот*'} | Stop-Process -Force" >nul 2>&1
timeout /t 2 /nobreak >nul
echo Проверка зависимостей...
python -m pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости!
    echo Попробуйте выбрать пункт 6 для ручной установки.
    echo.
)
start "Финансовый Telegram Бот" /min python bot.py
echo Бот перезапущен.
timeout /t 2 /nobreak >nul
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
    python -m pip install -r requirements.txt
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
python -m pip install -r requirements.txt
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

:diagnose_issues
cls
echo Диагностика проблем...
echo.
python check_config.py --diagnose
echo.
pause
goto menu

:troubleshooting
cls
echo Помощь по устранению неполадок:
echo ================================
echo.
echo Если кнопки не работают:
echo 1. Убедитесь, что запущен только один экземпляр бота
echo 2. Используйте пункт "Остановить бота", затем "Запустить бота"
echo 3. Проверьте логи на наличие ошибок
echo 4. Убедитесь, что токен бота указан правильно
echo.
echo Если бот не запускается:
echo 1. Проверьте установку зависимостей (пункт 6)
echo 2. Проверьте конфигурацию (пункт 7)
echo 3. Проверьте права доступа к файлам данных
echo.
echo Подробное руководство доступно в файле TROUBLESHOOTING.md
echo.
pause
goto menu

:exit
cls
echo Остановка бота и выход...
echo.
taskkill /f /im python.exe /fi "WINDOWTITLE eq Финансовый Telegram Бот*" >nul 2>&1
taskkill /f /im python.exe /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE ne Unknown Python Window" >nul 2>&1
wmic process where "name='python.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
powershell "Get-Process python | Where-Object {$_.MainWindowTitle -like '*Финансовый Telegram Бот*'} | Stop-Process -Force" >nul 2>&1
echo Спасибо за использование лаунчера!
echo.
pause
exit