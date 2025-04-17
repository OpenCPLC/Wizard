if ! pip show pyinstaller > /dev/null 2>&1; then
  pip install -U pyinstaller
fi
[ -f ./wizard-dist/wizard.exe ] && rm ./wizard-dist/wizard.exe
pyinstaller --onefile --workpath .wizard-build --distpath .wizard-dist --add-data "files;files" --name wizard --icon=opencplc.ico main.py
./wizard-dist/wizard.exe -v
