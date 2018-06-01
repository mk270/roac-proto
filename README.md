
Installation
============

One must install the database server, and set up a "virtual environment" for
the Python code. These installation instructions assume an Ubuntu Linux
environment, but should be easily adaptable.

Database
--------

The database should be hosted on Postgres and called `roac`. Thus:

    sudo apt-get install postgresql
    sudo -u postgres createuser $LOGNAME
    sudo -u postgres createdb roac
    psql roac -f schema.sql 

Virtual environment
-------------------

    sudo apt-get install python3-venv
    python3 -m venv myenv
    . myenv/bin/activate
    pip3 install setuptools --upgrade
    pip3 install -r requirements.txt

Test
----

    . myenv/bin/activate
    src/t/runtests.sh

