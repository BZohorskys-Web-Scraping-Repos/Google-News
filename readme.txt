README
======
Key:
    '>' = terminal command

Getting Started
---------------
    Setup virtual environment
    +++++++++++++++++++++++++
        Move to the top directory
            > cd <to the root project folder>
        Create virtualenv
            > python3 -m venv virtualenv
        Activate virtual environment
            > source virtualenv/bin/activate
        Install project dependencies
            > pip install -r requirements.txt

Run Project
-----------
    Activate virtual environment
    In the root directory:
        python launcher.py

Distribute Project
-------------
    pyinstaller launcher.py --name gnews --onefile
