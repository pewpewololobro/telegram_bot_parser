@echo off
call %~dp0parser API\venv\Scripts\activate
cd %~dp0parser API

set TOKEN=YOUR TOKEN
python bot_main.py

pause