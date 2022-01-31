# Exercise: Gustafson’s law
1. Assume a program with a serial fraction of 50%.
    - See Mathcad for the calculations.
    1. Compute the speed-up when using 2 and 4 processors according to Amdahl’s law.
        - 1.33 for 2 cores and 1.6 for 4 cores.
    1. Compute the speed-up when using 2 and 4 processors according to Gustafson’s law under the assumption that the parallel work per processor is fixed.
        - 1.5 for 2 cores and 2.5 for 4 cores.
    1. Why are both the speed-up results different?
        - Amdahl's calculates how much faster the problem can be solved with parallelism. The Gustaffson's calculates how much slower a sequential solution would be compared to the parallel solution.
        - For a more in-depth answer see the solution.
1. The analysis of a program has shown a speedup of 3 when running on 4 cores. What is the serial fraction according to Gustafson’s law?
    - See Mathcad.
    - The answer is 1/3.
