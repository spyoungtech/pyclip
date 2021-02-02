py -3.8 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install --upgrade wheel pytest coverage "codecov<5"
python -m pip install --upgrade .
call deactivate