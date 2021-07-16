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
        python gnews.py


Build Project
-------------
    Dev Test
    ++++++++
        Activate virtual environment
        Run setup.py
            > python setup.py develop
        An egg directory should have been created
        Test Tool
            > gnews

    Create .tar.gz file which can be install with pip
    +++++++++++++++++++++++++++++++++++++++++++++++++
        Activate virtual environment
        Run setup.py
            > python setup.py sdist bdist_wheel
        Test Tool
            Deactivate virtualenv
            pip install <path to .tar.gz file in dist dir>
