### Aggregates and Consistency Boundaries

#### Problem Statement:

- Currently, our system works fine because it is implemented as a single threaded system. In a multi-threaded system /
  multi-user application on introduction of concurrent access we might be allocating stock for multiple order lines
  simultaneously. We might even be allocating order lines at the same time as processing changes to the batches
  themselves.
- Think about scaling up our app, we realize that our model of allocating lines against all available batches may not
  scale.
    - To handle concurrent access issues we will have to apply locks and accessing Batch table for allocations we might
      end up getting a lock on the whole `Batches` table itself.
    - This will cause performance issues and cause deadlock conditions.
- We want to build a high performant system but also maintain the necessary invariants of our system.

#### Solution:

- We do not want to allocate Same product at the same time as it might cause concurrency problems, but we are fine with
  allocating different products at the same time.
- It’s safe to allocate two products at the same time because there’s no invariant that covers them both. We don’t need
  them to be consistent with each other.
- We make use of Aggregate Pattern to design a solution for this problem:
    - An aggregate is just a domain object that contains other domain objects and lets us treat the whole collection as
      a single unit.
    - An AGGREGATE is a cluster of associated objects that we treat as a unit for the purpose of data changes.
    - The aggregate will be the boundary where we make sure every operation ends in a consistent state.
    - Once you define certain entities to be aggregates, we need to apply the rule that they are the only entities that
      are publicly accessible to the outside world. In other words, the only repositories we are allowed should be
      repositories that return aggregates.