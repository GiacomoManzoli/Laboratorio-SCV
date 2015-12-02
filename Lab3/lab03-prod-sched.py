#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp
import sys
import json

#
# Optimization methods
#

# BRANCH AND BOUND
def branch_and_bound(solve_function, data,
                     time_limit = None):
    zbest, branches, time = solve_function(data, time_limit)
    print
    print '===============================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'THE PROBLEM WAS INFEASIBLE'
    print 'total number of branches is: %d' % branches
    print 'total time: %f' % time
    print '===============================================' 


# DESTRUCTIVE LOWER BOUNDING
def destructive_lb(solve_function, data, start, time_limit = None):
    zbest = None
    branches, time = 0, 0
    while zbest == None:
        print
        print '===============================================' 
        print 'Checking value %d for feasibility' % start
        print '==============================================='
        print
        zbest, br, tm = solve_function(data, time_limit = time_limit, ub = start)
        branches += br
        time += tm
        if zbest == None:
            start += 1
    print
    print '===============================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'THE PROBLEM WAS INFEASIBLE'
    print 'total number of branches is: %d' % branches
    print 'total time: %f' % time
    print '===============================================' 


# DESTRUCTIVE UPPER BOUNDING
def destructive_ub(solve_function, data, start, time_limit = None):
    zbest = start
    last_z = zbest
    branches, time = 0, 0
    while last_z != None:
        print
        print '===============================================' 
        print 'Searching for a solution within cost %d' % start
        print '==============================================='
        print
        last_z, br, tm = solve_function(data, time_limit = time_limit, ub = start)
        branches += br
        time += tm
        if last_z != None:
            zbest = last_z
            start = zbest - 1
    print 
    print '===============================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'THE PROBLEM WAS INFEASIBLE'
    print 'total number of branches is: %d' % branches
    print 'total time: %f' % time
    print '===============================================' 


# BINARY SEARCH
def binary_search(solve_function, data, start_lb, start_ub, time_limit = None):
    zbest = start_ub
    branches, time = 0, 0
    while zbest > start_lb+1:
        print
        print '===============================================' 
        print 'Searching for a solution with cost in [%d..%d]' % (start_lb, start_ub)
        print '==============================================='
        print
        last_z, br, tm = solve_function(data, time_limit = time_limit,
                                 lb = start_lb+1, ub = start_ub)
        branches += br
        time += tm
        if last_z != None:
            zbest = last_z
            start_ub = zbest - 1
        else:
            start_lb = start_ub + 1
    print 
    print '===============================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'THE PROBLEM WAS INFEASIBLE'
    print 'total number of branches is: %d' % branches
    print 'total time: %f' % time
    print '===============================================' 


#
# A FUNCTION TO BUILD AND SOLVE A MODEL
# time_limit: if None, not time limit is employed. If integer, a time limit is
#             enforced, but optimality is no longer guaranteed!
# lb:         lower bound
# ub:         upper bound
# 
# If both 'lb' and 'ub' are None, then Branch and bound is used for optimization
#
def solve_problem(data, time_limit = None, lb = None, ub = None):
    # Cache some useful data
    setups = data['setups']
    order_list = data['order_list']
    unit_list = data['unit_list']
    order_table = data['order_table']
    no = len(order_list)
    nu = len(unit_list)

    # Build solver instance
    slv = pywrapcp.Solver('production-scheduling')

    #
    # CREATE VARIABLES
    #
    # X i = t - Il prodotto i-esimo della lista unit_list viene prodotto all'istante t

    eoh = max(o['dline'] for o in order_list)

    x = []

    # creo una lista per ogni tipo di prodotto
    for i in range(0, nu):
        x.append(slv.IntVar(0,eoh,'Prod %d'%i))

    # Objective variable
    z = slv.IntVar(0,eoh)

    #
    # BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
    #

    # Vincolo 1
    # tutte le variabili diverse tra loro

    for i in range(0, nu):
        for j in range(i+1, nu):
            slv.Add(x[i] != x[j])

    # Vincolo 2
    # Per ogni prodotto, deve essere prodotto prima della sua deadline

    for i in range(0, nu):
        slv.Add(x[i] < unit_list[i]['dline'])

    # Vincolo 3
    # Minimizzare il makespan
    # z = max(start time)
    # z definition constraints

    slv.Add(z == slv.Max(x))

    # Vincolo 4
    # Attesa del set up
    # La differenza di due prodotti incompatibili deve essere diversa di 1
    # S_i + 1 != S_j con i e j incpmpatibili

    for i, u1 in enumerate(unit_list):
        for j, u2 in enumerate(unit_list):
            for setup in setups:
                p1 = setup[0]
                p2 = setup[1]
                if i != j and u1['prod'] == p1 and u2['prod'] == p2:
                    slv.Add(x[i] + 1 != x[j])

    # Questo modello ha tante soluzioni simmetriche
    # Se ho un blocco di prodotti che vengono prodotti in serie ci sono tante soluzioni
    # simili che vanno a far aumentare la dimensione dell'albero
    # E' possibile inserire dei vincoli per rompere queste simmetrie ed ottenere 
    # delle prestazioni molto migliori

    for i, u1 in enumerate(unit_list):
        for j, u2 in enumerate(unit_list):
            if u1['prod'] == u2['prod'] and u1['dline'] == u2['dline'] and i < j:
                slv.Add(x[i] > x[j])

    # Anche quando si forzano le simmetrie, la scelta influisce sulle presstazione
    # ad esempio usare il > porta ad esploare meno branch rispetto il <

    # Optional bounding constraints
    if lb != None:
        slv.Add(z >= lb)
    if ub != None:
        slv.Add(z <= ub)

    #
    # THOSE ARE THE VARIABLES THAT WE WANT TO USE FOR BRANCHING
    #
    all_vars = x

    # DEFINE THE SEARCH STRATEGY
    decision_builder = slv.Phase(all_vars,
                                 slv.INT_VAR_DEFAULT,
                                 slv.INT_VALUE_DEFAULT)

    # INIT THE SEARCH PROCESS

    # log monitor (just to have some feedback)
    # search_monitors = [slv.SearchLog(500000)]
    search_monitors = []
    # enforce a time limit (if requested)
    if time_limit:
       search_monitors.append(slv.TimeLimit(time_limit))
    # enable branch and bound
    if lb == None and ub == None:
        search_monitors.append(slv.Minimize(z, 1))

    # init search
    slv.NewSearch(decision_builder, search_monitors)

    # SEARCH FOR A FEASIBLE SOLUTION
    zbest = None
    while slv.NextSolution():
        #
        # PRINT SOLUTION
        #

        #### YOUR STUFF HERE ####

        #
        # STORE SOLUTION VALUE
        #
        zbest = z.Value()

        # If not in branch & bound mode, stop after a solution is found
        if lb != None or ub != None:
            break

    # print something if no solution was found
    if zbest == None:
        print '*** No solution found'

    # print stats
    branches, time = slv.Branches(), slv.WallTime()
    print '*** Number of branches: %d' % branches
    print '*** Computation time: %f (ms)' % time
    if time_limit != None and slv.WallTime() > time_limit:
        print '*** Time limit exceeded'

    # END THE SEARCH PROCESS
    slv.EndSearch()

    # Return the solution value
    return zbest, branches, time


# LOAD PROBLEM DATA
if len(sys.argv) != 2:
    print 'Usage: python %s <data file>' % sys.argv[0]
    sys.exit()
else:
    fname = sys.argv[1]

with open(fname) as fin:
    data = json.load(fin)


#
# CALL THE SOLUTION APPROACH
#
# branch_and_bound(solve_problem, data)
# destructive_lb(solve_problem, data, start = #### YOUR STUFF HERE ####)
# destructive_ub(solve_problem, data, start = #### YOUR STUFF HERE ####)
# binary_search(solve_problem, data,
#               start_lb = #### YOUR STUFF HERE ####,
#               start_ub = #### YOUR STUFF HERE ####)