# capstone
The Real Time Portfolio Analytics Software

In order to run this application, please follow the instructions below

1. Install Anaconda (https://www.continuum.io/downloads) 
Install for Python 2.7

2. Install PyCharm
 (https://www.jetbrains.com/pycharm/download/#section=windows) 

3. Install Git (https://git-scm.com/downloads)
You can also install Github desktop.
Clone the project from my repository to yours


4. Copying anaconda environment from my environment.yml file
In the terminal, run -

Conda env create -f environment.yml 

to create the environment with the same packages

5. Copy and paste .gitignore 
(https://github.com/github/gitignore/blob/master/Global/JetBrains.gitignore) copy and paste under the project folder (should be called capstone)

6. Setup Project Interpreter
File -> Settings -> Project Interpreter (from pycharm)

7. Install other packages
a. Cvxopt conda install -c omnia cvxopt
b. CVXPY (http://www.cvxpy.org/en/latest/install/)
c. Multiprocessing import error can be solved by: (https://github.com/uqfoundation/multiprocess/commit/02c1480e3e0a8d6740a2234f1f757d8d90dc7705)


Install the packages

In the terminal, run - 
    Conda install Flask
    Pip install Flask-SQLAlchemy

Install PostgreSQL 
a. Windows (http://www.enterprisedb.com/products-services-training/pgdownload#windows)
b. Mac (http://postgresapp.com/) 
c. List of GUI tools
      Add “C:\Program Files\PostgreSQL\9.6\bin” to the PATH variables
      Right click database -> New database
d. Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/ search for psycopg and download it to \Anaconda\envs\py27an400\Lib\site-packages
Search for Psycopg2, download the wheel,
Then in the terminal, run -
  Pip install ___.whl




