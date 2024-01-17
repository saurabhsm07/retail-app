#### Problem statement:

- presently our Service layer is dependent on Session and as well as abstract repository and hance is coupled with the
  data layer
    - allocate(order_line: OrderLine, repository: AbstractRepository, session):

- because of this we have to instantiate a session from our Flaks API module and then pass it to the service along with
  the repository
  Solution:
- we create another layer of abstraction called unit of work which will manage session creation and returning to us (
  service) a repository object thus collaborating with the Repository
- we make use of unit of work design pattern to decouple our service layer from the data layer.
    - which means neither the service layer nor the API layer directly communicates with the datalayer.

#### Solution:

#### Approach:

- We define a class abstract class AbstractBatchUnitOfWork.
- Define batches (class var), which will give us access to the batches repository.
- This implementation is to be used with a context manager (with) hence we define dunder `enter` and `exit` methods as
  well.
- `rollback` and `commit` methods are also implemented.
