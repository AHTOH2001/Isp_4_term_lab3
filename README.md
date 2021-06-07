# Third lab work ISP

### Docker-compose running:

1. In terminal `docker-compose up`
2. Attention: Server will be available on 127.0.0.1:8080

### Installing, deployment and running manual:

1. Install requirements using command `python3 -m pip install -r requirements.txt`
2. Install a local database or use remote one, it could be any popular database that supports JSON fields
3. In the file `config.py` specify connection and engine of your database, more
   details [here](https://docs.djangoproject.com/en/3.1/ref/settings/#databases), also additionally you can specify some
   more details like language code, time zone and allowed hosts
4. Switch to the folder `shop` and make migrations using command `python3 manage.py makemigrations`, and then migrate
   them using command `python3 manage.py migrate`
5. Run server using command `python3 manage.py runserver 127.0.0.1:8080`, than if you wish you can stop service
   using `ctrl+C`

### Tests running manual:

Firstly you should successfully install service by passing first 3 steps on installing, deployment and running manual,
and if you done them properly you can run tests using command `python3 manage.py test` successful result looks like
that:

```commandline
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........
----------------------------------------------------------------------
Ran 10 tests in 0.351s

OK
Destroying test database for alias 'default'...
```

To calculate coverage you can use command `coverage run --source='shop' shop/manage.py test mainapp`

Result will look like:`

```commandline
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...................
----------------------------------------------------------------------
Ran 19 tests in 3.087s

OK
Destroying test database for alias 'default'...

(venv) D:\Ucheba\Labs\term_4\Yandex\project>coverage report
Name                                                 Stmts   Miss  Cover
------------------------------------------------------------------------
shop\config.py                                          29      0   100%
shop\mainapp\__init__.py                                 0      0   100%
shop\mainapp\admin.py                                    8      0   100%
shop\mainapp\apps.py                                     3      3     0%
shop\mainapp\forms.py                                   76      7    91%
...
shop\mainapp\views\RestAPI.py                          125     10    92%
shop\mainapp\views\__init__.py                           2      0   100%
shop\mainapp\views\frontend.py                         195     99    49%
shop\manage.py                                          12      2    83%
shop\shop\__init__.py                                    0      0   100%
shop\shop\asgi.py                                        4      4     0%
shop\shop\settings.py                                    1      0   100%
shop\shop\urls.py                                        3      0   100%
shop\shop\wsgi.py                                        4      4     0%
------------------------------------------------------------------------
TOTAL                                                  814    138    83%

```


