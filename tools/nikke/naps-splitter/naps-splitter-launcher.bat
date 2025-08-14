@echo off

if exist "./aeb" rmdir /s /q "./aeb"
mkdir "./aeb"

start /b node naps-splitter-shell-arg.js 0
start /b node naps-splitter-shell-arg.js 1
start /b node naps-splitter-shell-arg.js 2
start /b node naps-splitter-shell-arg.js 3
start /b node naps-splitter-shell-arg.js 4
start /b node naps-splitter-shell-arg.js 5
start /b node naps-splitter-shell-arg.js 6
start /b node naps-splitter-shell-arg.js 7
start /b node naps-splitter-shell-arg.js 8
start /b node naps-splitter-shell-arg.js 9
start /b node naps-splitter-shell-arg.js a
start /b node naps-splitter-shell-arg.js b
start /b node naps-splitter-shell-arg.js c
start /b node naps-splitter-shell-arg.js d
start /b node naps-splitter-shell-arg.js e
start /b node naps-splitter-shell-arg.js f

echo Waiting for all processes to complete...
timeout /t 2 /nobreak >nul

:wait_loop
tasklist /fi "imagename eq node.exe" 2>nul | find /i "node.exe" >nul
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

echo done
