# How to run the algorithms:
- `bully-election.py` and `hirschberg-sinclair.py` can be run through the terminal through the following command:<br>
`mpiexec -n <#-nodes> --use-hwthread-cpus --oversubscribe python <file-name>`
  - It starts the given amount of nodes and runs the given file. 
    - `--use-hwthread-cpus` allows us to utilize the hardware threads in our CPU.
    - `--oversubscribe` allows us to start more processes than we have ressources available.