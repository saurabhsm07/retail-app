-   currently tests are tightly coupled for object creation related tasks, unable to run them independently. Need to decouple them.
  - SOLUTION: Fixed with default_factory from dataclasses
  
-   Currently placing orm as as a single module in src folder 
  - SOLUTION: Moved orm module to adapters package

- Building a fake repository in our repository pattern, I can see how its built I am yet to understand its usage. 
  - SOLUTION: check service layer tests and how the fake repository is used in it along with dependency injection to facilitate simple unit testing

- Currently facing issues in properly starting a Flask Application inside docker container and running tests against it 
  - SOLUTION: found a workaround for it check .scripts/tests.sh file and readME for info

- allocate and deallocate API endpoints not updated to use Unit of Work pattern

- No test object deletion logic implemented as part of test_repository.

- No Dev notes collected as part of Aggregate pattern and consistency boundaries

- Exhaustive unit tests for UOW required.

-  At present we have not integrated any database with our project and that handicaps us when dealing / testing
    race conditions / concurrency control code.
    UPDATE: Integrated postgres DB but these tests still fail. **

