# pip install -U pyinstaller
[ -f ./wizard-dist/wizard.exe ] && rm ./wizard-dist/wizard.exe
pyinstaller --onefile --workpath wizard-build --distpath ./wizard-dist --icon=logo.ico wizard.py
./wizard-dist/wizard.exe -v