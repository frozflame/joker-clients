joker-clients
=============

simple clients for simple and dedicated services

Develop
-------

Get code

    git clone ssh://git@github.com/frozflame/joker-clients.git
    cd joker-clients

Install requirements

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -e .

Run tests

    pip install -U pytest joker
    pytest -vs tests/

Code quality check

    pip install flake8
    flake8 joker/

Symlink `pre-commit` script

    (cd .git/hooks; ln -sf ../../tests/dev/pre-commit)

