# Exercise: RAFT
1. What is a "term" in RAFT and what are "terms" used for?
   - A term in RAFT is time period where a certain server is a designated leader. There may be terms where no leader is found, which immediately starts a new term.
   - Terms are used for keeping track of which state the current candidate is on. It is also used for classifying the logs and used during leader election.
1. How is leader election done in RAFT?
   - Through random timers and basically bully election.
1. What does RAFT do, if there is a split vote in a term?
   - Wait for a new timer to expire.
1. How is log replication done in RAFT?
   - The leader tries to send the newest log to all followers in the system.
1. How does RAFT guarantee logs to be replicated correctly?
   - It only allows actions to be committed if a majority of the system has agreed on it. Only then is the action response sent to the client.
1. How does RAFT resolve log inconsistencies and what role does the "log matching property" play?
   - See slide 26.
1. What criterion needs to be fulfilled for a node to become leader in RAFT?
    - It must have an up-to-date log to be electible, it must have the highest term and the majority of the votes.
      - (It increments the term on candidate promotion, so if it was on current term before the promotion it will be the highest term after promotion)
1. How does RAFT reach consensus in a distributed system (what criterion needs to be fulfilled)?
    - In order for an action to be executed and thereby a log to be committed, the majority needs to agree on it.
1. How can RAFT help provide fault tolerance in distributed systems?
    - Since the system will continue even if one server fails (it is just a partial failure), faults are not necessarily critical, and thereby the system is more fault tolerant. 
1. What does the RAFT acronym stand for and who developed RAFT?
    - Replicated and fault tolerant.
    - Diego Ongaro and John Ousterhout from Stanford University. 2014.

    