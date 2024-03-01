# retail-app

### python web app development following TDD approach.

Following the steps detailed in the book:

```
Architecture Patterns with Python
by Harry Percival, Bob Gregory
``` 

### SETUP:

- Install Docker, for windows installation follow:
    - docker installation steps: https://docs.docker.com/desktop/install/windows-install/
    - Windows subsystem for Linux: https://learn.microsoft.com/en-us/windows/wsl/install
- use Make file with WSL shell to:
    - build container image
    - execute test suite
    - open shell
  
### INITIALIZATION:  

Set *FLASK_APP* env variable  as per your OS, virtual env and start server local as below
```
FLASK_APP=src/entrypoints/flask_app.py 
flask run --host=0.0.0.0 --port=80
```
### Running Test Suite:  
- Option 1: local system run
  - Create a python virtual env with packages detailed in `Pipfile`
  - Start a Flask App server with commands detailed  **INITIALIZATION** steps and run the test suite locally using pytest commands.
  - Additional environment variables that need to be specified:  
    - `ENV=dev or local` : tests to be executed in LOCAL mode (against SQLITE DB) or DEV mode (POSTGRES DB).
    - `DB_HOST=<HOST-NAME>` : host name of the database server, in case of ENV=DEV.
- Option 2: Follow the **SETUP** Steps and run using docker container and use command `make run-tests`.
  - `ENV=dev or local` : tests to be executed in LOCAL mode (against SQLITE DB) or DEV mode (POSTGRES DB).

### ISSUES 
- Some tests are not atomic in nature. Mostly ORM and Repository tests and create junk data.
- Race condition / Concurrency tests fail.


### DISCLAIMERS:  
- Running the docker file will not automate a container and start a web application.


### UPDATES:

- updated python version to `3.11` because in the older version of `3.8` pipenv virtual environment was raising SSL
  exceptions during package installation.

### Workarounds:

- Suffixed `Flask RUN` command with `&` in **tests.sh** bash script to avoid blocking current run on flask server start.
    - NOTE: Delete the local sql lite db file manually before running unit tests against the docker container.

- ORM tests are basic in nature and fail on foreign key constraints. As a result they are skipped when executin in DEV (with postgre DB)