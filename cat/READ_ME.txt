*INSTALLATION INSTRUCTIONS*

1. Create a conda env using 'requirements.txt'.
2. Setup a working PostgreSQL
3. Update the following files with YOUR details

'..\cat\sql\database\init.sql'
'..\cat\R\lib\postgresql.R'
'..\cat\python\lib\sql\postgresql\postgresql.py'
'..\cat\python\lib\api\alpha\alpha.py'
'..\cat\python\lib\api\valr\valr.py'
'..\cat\cat.bat'

4. Run sql.init (..\cat\sql\database\init.sql), to setup the db and tables.
5. Install R & RStudio (IDE).

6. You're ready to go, just run the following scipts in the conda env created in 1., in the following order (or replace with step 8.):

1ping.py
2process.py
3fetch.py

7. View the results directly in PostgreSQL, or run '..\cat\R\app.R'
8. Update 'cat.bat' with correct absolute paths. You can double-click this file, or schedule it, and it will replace step 6.

* If you run into any issues, please contact christopherrconrady@gmail.com