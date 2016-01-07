rem delete python cache files and eric project cache files
for /f %%i in ('dir __pycache__ /s /b /a:d') do rd "%%i" /s /q
for /f %%i in ('dir _eric6project /s /b /a:d') do rd "%%i" /s /q
