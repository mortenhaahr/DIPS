# Exercise: Consensus and fault tolerance
1. Discuss the need for fault tolerant systems and how fault tolerance is achieved in distributed systems
   - Redundancy. 
1. Discuss the fault consequences related to: i) availability, ii) reliability, iii) safety, iv) maintainability
    - Availability: Probability that a system is working correctly. Measured with percentage time it is actually available.
    - Reliability: Often measured in mean time between failure (MTBF). Unlike availability it doesn't care about how long the failure actually took to repair. It cares more about how often a failure occurs instead of how long the system is down for.
    - Safety: Does something catastrophic happen when a failure occurs.
    - Maintainability: How easy is it to repair the system after a failure.
1. Discuss the failure types: i) crash failure, ii) omission failure, iii) timing failure, iv) response failure and v) arbitrary failure
    - Crash failure: The system appears to be working correctly, until the system suddenly halts.
    - Omission failure: Fails to respond to incoming requests. Can either be receive- or send omission failures.
    - Timing failure: Response lies outside a specified time interval
    - Response failure: Response is incorrect. Either because of an incorrect value or because there is a state-transition error (incorrect control flow)
    - Arbitrary failure: Random error that makes no sense.
1. What is “consensus” in relation to distributed systems and why is it desirable to be able to guarantee consensus?
    - From literature from week 3:
      - Several computers (or nodes) achieve consensus if they all agree on some value. More formally:
        1. Agreement: Every correct process must agree on the same value.
        2. Integrity: Every correct process decides at most one value, and if it decides some
        value, then it must have been proposed by some process.
        1. Termination: All processes eventually reach a decision.
        2. Validity: If all correct processes propose the same value V, then all correct processes decide V.
1. What fundamental property is typically needed in order to reach consensus (e.g. in terms of quorum)?
    - From slide 8 for todays lecture:
    ```
    Consensus algorithms (overall principles):
    » Approaches to solve the consensus problem
    » E.g. reliable data or state machine replication in dist. systems
    » Designed to deal with limited numbers of faulty processes
    » An algorithm that can correctly guarantee consensus amongst
    n processes of which at most t fail is said to be t-resilient
    » Time, space and message complexity are typical performance
    metrics
    Christian Fischer Pedersen, Electrical and Computer Engineering, Aarhus University 8]29
    ```
