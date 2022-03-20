# Questionnaire App

Before running the app assuming that **python 3.8.xx** is installed on development machine

1. Create virtual environment with python3.8.xx
```shell
python3.8 -m venv env
```
2. Activate the virtual environment
```shell
source env/bin/activate
```
3. Install requisite packages:
```shell
pip install -r requirements.txt
```

4. Adjust the configurations for database under **social_questionnaire/configs/db.cnf** folder

5. Run the migrations to reflect the django models to mysql database
```shell
python manage.py migrate
```

6. Run Server Locally
```shell
python manage.py runserver
```

7. Create Superuser for Admin-panel
```shell
python manage.py createsuperuser
```

8. Create the questions answers from admin panel

9. Urls Information:

```shell
open http://localhost:8000/friend-ship-test/create-test/
open http://localhost:8000/friend-ship-test/test-comparison/test-uuid/
open http://localhost:8000/admin
```

10. Screenshots under screenshots folder