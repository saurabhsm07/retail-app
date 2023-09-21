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

### UPDATES:

- updated python version to `3.11` because in the older version of `3.8` pipenv virtual environment was raising SSL
  exceptions during package installation.

### Workarounds:

- Suffixed `Flask RUN` command with `&` in **tests.sh** bash script to avoid blocking current run on flask server start.
    - NOTE: Delete the local sql lite db file manually before running unit tests against the docker container. 