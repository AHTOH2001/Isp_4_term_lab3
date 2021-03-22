# Project for Yandex backend school

### Installing, deployment and running manual:
1. Install requirements using command `python3 -m pip install -r requirements.txt`
2. Install a local database or use remote one, it could be any popular database that supports JSON fields
3. In the file `./mainapp/shop/settings.py` specify connection and engine of your database, more details [here](https://docs.djangoproject.com/en/3.1/ref/settings/#databases), also additionally you can specify some more details like language code, time zone and allowed hosts
4. Switch to the folder `shop` and make migrations using command `python3 manage.py makemigrations`, and then migrate them using command `python3 manage.py migrate`
5. Run server using command `python3 manage.py runserver 0.0.0.0:8080`, than if you wish you can stop service using `ctrl+C` 

### Tests running manual:
Firstly you should successfully install service by passing first 3 steps on installing, deployment and running manual, and if you done them properly you can run tests using command `python3 manage.py test` successful result looks like that: 
```commandline
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........
----------------------------------------------------------------------
Ran 10 tests in 0.351s

OK
Destroying test database for alias 'default'...
```




