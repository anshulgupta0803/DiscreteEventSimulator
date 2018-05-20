# DiscreteEventSimulator

Taking advantage of the power of simulation analysis and model behaviours that are difficult to capture using theoretical queuing systems and Markov chain models.

## System Characterstics
- Multi-core server machine with thread-to-core affinity (once a thread is "assigned" to a core, it will remain there)
- Multi-threaded Web server
- Thread-per task model - until max is reached, after which queuing for threads starts. 
- Round-robin scheduling, with context-switching overhead
- Request time-outs
- Users are in a standard closed loop - issue request, wait for response, think then issue request again.

