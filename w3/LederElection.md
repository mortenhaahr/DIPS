# 1. In general, why and when is leader election relevant in distributed systems?

Things will fail, so you need a way to reelect a leader in case the leader malfunctions.

Also needed at initialization, or chaos can ensue.



### (a) Discuss applications that would / would not work without leader election.

Aggregation of data - who does the aggregation? Who sends the result?

Internet.

IoT.



# 2. Does leader election entail a computational and/or network burden?

Yes

### (a) If so, how can time complexity be used as a metric for the computational burden?

If it takes a long time to elect a leader, that is more time spent NOT solving the problem.

More time spent waiting even though a node may be ready for new work.

### (b) If so, how can message complexity be used as a metric for the network burden

More message complexity = Higher bandwidth usage.

More message complexity = More time spent on handling messages.

# 3. Discuss the mechanics of the presented leader election algorithms, e.g. by considering

### (a) Concretely, how do they function?

Bully: Choose the one with the highest ID. Send messages to the nodes with higher ID's only. Very bad worst case!

LCR: Ring configuration. Send to all nodes in a clockwise direction. All results aggregate to the initial node, who broadcasts the result to all nodes. Multiple elections can be underway at the same time.

MAH: Tree structure (Minimum spanning tree). Parent is the first node a election message was received from.  Results are aggregated on the response of the children nodes. The leader is elected by the base node and the result is broadcasted.

HS: Ring structure. Starts with broadcast. All members then initiate a candidacy. All the nodes with higher ID will kill lower ID messages, so that only the highest ID messages will survive. Phase and k number is in the messages to ensure no message oscillation.

### (b) What is their scope of applicability (i.e. their problem and application domains)?

MAH: Mobile ad hoc networks... It is in the name! Useful when the nodes have resources that has measurability. Nodes can move without problem. 

Bully: Few nodes. Worst case performance is shit, so if this metric is important then do not choose this. All nodes must be in range of each other.

LCR: All nodes must know the ring structure. You should probably use this instead of bully in most cases. Nodes can be in range of some nodes and the network will still work. High time complexity, low message complexity.

HS: A lot of back and forth between the nodes. Scales exponentially, which is quite nice. 

### (c) Discuss pros and cons of competing algorithms

See (b)

# 4. Bully Election

### (a) Derive the message complexity
We are looking at worst case and assuming all nodes are online.

**Election messages:**

$(N-1) + (N-2) ... (N-(N-1)) = \textbf{(N-1)*N/2}$ since $(1 + (N-1))$ = N. This happens N/2 times.

This equals: O(N*N/2) Which in big O is: O(N^2)

For dummies:
- System of N = 5 processes.
- P0 sends to 4 others. (N-1)
- P1 sends to 3 others. (N-2)
- P2 sends to 2 others. (N-3)
- P3 sends to 1 others. (N-4)
- P4 sends to 0 others. (N-5) = N-N.
  
Comparison:
- 4+3+2+1 = 10.
- $\frac{(N-1)*N}{2} = \frac{N*N-N}{2} = \frac{5^2 - 5}{2} = 20/2 = 10$

**Acknowledgement messages:**
Same as election

**Leader broadcast:**

Always N-1.

**Total:**

Combined this becomes: $N^2 - 1$

### (b) Implement the algorithm (preferably in Python) and verify it works

### (c) Use the implementation to demonstrate the message complexity in practice
We counted how many messages were received of each category.