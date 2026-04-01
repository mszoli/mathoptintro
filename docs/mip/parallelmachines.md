---
tags:
  - mip
  - scheduling
  - logic-based benders decomposition
  - big-m formulation
---

# Unrelated Parallel Machine Scheduling Problem

In this section, we consider an unrelated parallel [machine scheduling problem](../intro/scheduling.md) with machine- and sequence-dependent setup times.
We present a MIP formulation for the problem, then apply a **Logic-Based Benders Decomposition** (*LBBD*) solution approach.

!!! quote "Decomposition methods for the parallel machine scheduling problem with setup"
    Tran, T. T., Araujo, A., & Beck, J. C. (2016).
    *Decomposition methods for the parallel machine scheduling problem with setups*.
    INFORMS Journal on Computing, 28(1), 83-95.

## Problem formulation

A set $\mathcal{J}$ of *jobs* must be processed on a set $\mathcal{M}$ of *machines*, such that each job must be assigned to and processed on exactly one machine.
The *processing time* of job $j$ on machine $i$ is denoted by $p_{ij}$.

There are *machine- and sequence-dependent* ***setup times***:
$s_{ijk}$ denotes the time that must elapse between the completion of job $j$ and the start of the consecutive job $k$ on machine $i$.
If job $k$ is the first job processed on machine $i$, then the required setup time is denoted by $s_{i0k}$.

The objective is to minimize the *makespan* of the schedule, i.e., the *completion time* of the last job.

Parameter | Description
--- | ---
$\mathcal{J} = \{1,\ldots,n\}$ | set of jobs
$\mathcal{M} = \{1,\ldots,m\}$ | set of machines
$p_{ij}$                       | processing time of job j on machine i
$s_{ijk}$                      | setup time from job $j$ to job $k$ on machine $i$
$s_{i0k}$                      | setup time for the first job $k$ on machine $i$

## MIP formulation

It will be convenient to extend the set of jobs with a *dummy job*, $\mathcal{J}^+ = \mathcal{J} \cup \{0\}$, which is assigned to each machine as the first job.

### Variables

Let the binary *assignment variable* $\mathbf{x}_{ij}$ indicate whether job $j$ is processed on machine $i$, and let the binary *precedence variable* $\mathbf{y}_{ijk}$ indicate whether job $k$ is processed directly after job $j$ on machine $i$.
Note that the $\mathbf{y}_{ijk}$ variables alone would be sufficient to formulate the problem (since the $\mathbf{x}$-variables can be expressed in terms of them), but the LBBD approach will be based on this formulation.

Variable | Domain | Description
--- | --- | ---
$\mathbf{x}_{ij}$   | $\{0,1\}$            | indicates whether job $i$ is processed on machine $i$
$\mathbf{y}_{ijk}$  | $\{0,1\}$            | indicates whether job $k$ is processed directly after job $j$ on machine $i$
$\mathbf{z}_i$      | $\mathbb{R}_{0\leq}$ | total setup time on machine $i$
$\mathbf{C}_j$      | $\mathbb{R}_{0\leq}$ | completion time of job $j$
$\mathbf{C}_{\max}$ | $\mathbb{R}_{0\leq}$ | makespan (i.e., maximum completion time)

### Objective

The obejctive is to minimize the makespan:

$$
\operatorname{minimize}\ \mathbf{C}_{\max}
$$

### Constraints

Each (real) job is assigned to exactly one machine:

$$
\begin{equation}
\sum_{i\in \mathcal{M}} \mathbf{x}_{ij} = 1 \quad\ \text{for all}\ j \in \mathcal{J}
\end{equation}
$$

The dummy job is assigned to all machines:

$$
\begin{equation}
\mathbf{x}_{i0} = 1 \quad\ \text{for all}\ i \in \mathcal{M}
\end{equation}
$$

Each job has exactly one predecessor and one successor on the assigned machine:

$$
\begin{equation}
\mathbf{x}_{ik} = \sum_{j \in \mathcal{J}^+} \mathbf{y}_{ijk} \quad\ \text{for all}\ i \in \mathcal{M},\ k \in \mathcal{J}^+
\end{equation}
$$

$$
\begin{equation}
\mathbf{x}_{ij} = \sum_{k \in \mathcal{J}^+} \mathbf{y}_{ijk} \quad\ \text{for all}\ i \in \mathcal{M},\ j \in \mathcal{J}^+
\end{equation}
$$

Total setup time on machines:

$$
\begin{equation}
\mathbf{z}_i = \sum_{j \in \mathcal{J}^+}\sum_{k \in \mathcal{J}^+} s_{ijk}\mathbf{y}_{ijk} \quad\ \text{for all}\ i \in \mathcal{M}
\end{equation}
$$

The makespan is the maximum of makespan of the machines:

$$
\begin{equation}
\mathbf{z}_i + \sum_{j \in \mathcal{J}} p_{ij}\mathbf{x}_{ij} \leq \mathbf{C}_{\max} \quad\ \text{for all}\ i \in \mathcal{M}
\end{equation}
$$

Jobs cannot overlap each other:

$$
\begin{equation}
\mathbf{C}_k \geq \mathbf{C}_{j} + s_{ijk} + p_{ik} + \operatorname{M}(1-\mathbf{y}_{ijk}) \quad\ \text{for all}\ i \in \mathcal{M},\ j \in \mathcal{J}^+,\ k \in \mathcal{J}
\end{equation}
$$

where $\operatorname{M}$ is an appropriately big constant, and

$$
\mathbf{C}_0 = 0
$$

## Logic-Bender Based Decomposition

### Master problem

Consider the following relaxation of the **original problem**, called **master problem**:

$$
\begin{aligned}
\operatorname{minimize}\ \mathbf{C}_{\max} & \\
\text{constraints}\ (1)-(6) & \\
\mathbf{x}_{ij} \in \{0,1\}    & \quad\ \text{for all}\ i \in \mathcal{M},\ j \in \mathcal{J} \\
0 \leq \mathbb{y}_{ijk} \leq 1 & \quad\ \text{for all}\ i \in \mathcal{M},\ j \in \mathcal{J}^+,\ k \in \mathcal{J}^+
\end{aligned}
$$

### Subproblem

Let $(\bar{x},\bar{y},\bar{z},\bar{C}_{\max})$ be the optimal solution for the master problem.
Since the $\mathbf{x}$-variables are still integer, each job is assigned to exactly one machine.
However, due to the relaxation, jobs may overlap.

Construct a solution to the original problem by solving the following **subproblem** for each machine $i$: schedule the assigned jobs $\mathcal{J}^i = \{ j \in \mathcal{J}\ :\ \bar{x}_{ij} = 1 \}$ minimizing the makespan $C_{\max}^i$.
Clearly, the constructed solution is feasible for the original problem with makespan equals to $\max_{i\in\mathcal{M}} C_{\max}^i$

If $\max_{i\in\mathcal{M}} C_{\max}^i \leq \bar{C}_{\max}$, then, the constructed solution is optimal to the the original problem.

Otherwise, $C_{\max}^i > \bar{C}_{\max}$ for some machine $i$, and thus the constructed solution is not necessarily optimal for the original problem.
Therefore, we add a so-called **Benders cut** *on the objective function* to the master problem, and resolve it.

Our candidate constraint is of the following form:

$$
\mathbf{C}_{\max} \geq C_{\max}^i - \sum_{j \in \mathcal{J}^i} \operatorname{M}_j(1 - \mathbf{x}_{ij})
$$

where each $\operatorname{M}_j$ is an appropriately large constraints.

The idea is that if all the jobs $\mathcal{J}^i$ are assigned to machine $i$ (i.e., $\mathbf{x}_{ij} = 1$ for each $j \in \mathcal{J}^i$), then $\mathbf{C}_{\max} \geq C_{\max}^i$ is forced.
Clearly, the choice $\operatorname{M}_j := C_{\max}^i$ for all $j$ is appropriate, but we can do better!

Let $\operatorname{M}_j := p_{ij} + \max\{ s_{ikj}\ :\ k \in \mathcal{J}^i \}$ be the processing time of job $j$ and the maximum setup time.
One can show that - if the setup times satisfy the triangle inequality - the proposed cut does not remove any globally optimal solution.

### Solution procedure

``` mermaid
flowchart LR
    Start([start]) --> BuildMaster[build master problem]
    BuildMaster --> SolveMaster[solve master problem]
    SolveMaster --> SolveSub[solve subproblems]
    SolveSub --> AllFeasible{all feasible?}
    AllFeasible -- yes --> Stop([stop])  
    AllFeasible -- no --> BendersCut["Add Benders-cut(s)<br>from infeasible subproblem(s)"]
    BendersCut --> SolveMaster
```

## Implementation

The implementation of the models can be found in <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/parallelmachines.py" target="_blank">`parallelmachines.py`</a>