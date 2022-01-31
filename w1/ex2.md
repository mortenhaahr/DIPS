# Exercise: Amdahl’s law
1. If there is a tight sequential coupling between steps in a computational problem it is called *inherently serial*. What is the serial fraction, f , in such a problem?
    - In that case f = 1 and the problem cannot be optimized through parallelization.
1. If there is no sequential coupling between steps in a computational problem it is called perfectly parallel (also called embarrassingly parallel). What is the serial fraction, f , in such a problem?
    - The execution time will go towards 0.
1. What is the theoretical speedup in execution latency of a program if 25% of the original execution time is made twice as fast?
    - Calcs:
        - f = 0.75
        - 1 - f = 0.25
        - 1/(f + (1-f)/P) = 1.143
    - It is 14.3 % faster.
1. The analysis of a program has shown a speedup of 3 when running on 4 cores. What is the serial fraction (best case) according to Amdahls law?
    - Through isolation of f in Amdahls law, where f is unknown and P = 3:
        - 3 = 1/(f + (1-f)/4)  => f = 1/9
1. Assume 10%, 20%, and 50%, respectively, of a program’s run-time is non-parallelizable and the program is supposed to run on a super-computer with 100000 cores. Also, assume that the program runs at the same speed on all of the cores, and there are no additional overheads. Plot a graph that illustrates the theoretical parallel speedup as a function of number of cores.
    - See Mathcad.
1. Assume 0.1% of a program’s run-time is non-parallelizable, that the program is supposed to run on a super-computer with 100,000 cores, and that the program runs at the same speed on all of the cores. Assume also that the program invokes a broadcast operation which adds overhead as a function of the number of cores involved. There are two broadcast implementations available. One adds a parallel overhead of BC1OH (P ) = 0.0001P , and the other adds BC2OH (P ) = 0.0005 log(P ). Find, for each of the broadcast implementations, the number of cores that maximizes the speed-up.
    - See Mathcad.