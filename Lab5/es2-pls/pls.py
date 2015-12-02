#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp
import sys
import json
import math

#
# A FUNCTION TO BUILD AND SOLVE A MODEL
# time_limit: if None, not time limit is employed. If integer, a time limit is
#             enforced, but optimality is no longer guaranteed!
#
def solve_problem(data, time_limit = None):
    # Cache some useful data
    matrix = data['matrix']
    n = len(matrix)

    # Build solver instance
    slv = pywrapcp.Solver('production-scheduling')

    # One variable for each cell
    x = {(i,j) : slv.IntVar(0, n-1, 'x[%d,%d]' % (i,j)) for i in range(n)
                                                for j in range(n)}

    # All different values on each row
    for i in range(n):
        row = [x[i,j] for j in range(n)]
        slv.Add(slv.AllDifferent(row, True))

    # All different values on each column
    for j in range(n):
        col = [x[i,j] for i in range(n)]
        slv.Add(slv.AllDifferent(col, True))

    # Pre-filled cells
    for i in range(n):
        for j in range(n):
            if matrix[i][j] >= 0:
                slv.Add(x[i,j] == matrix[i][j])

    # DEFINE THE SEARCH STRATEGY
    decision_builder = slv.Phase(x.values(),
                                 slv.CHOOSE_MIN_SIZE_LOWEST_MIN, # scelgo la variabile e il valore che 
                                 slv.ASSIGN_MAX_VALUE)           # e' piu' facile che porti ad una sol. infeasible

    # INIT THE SEARCH PROCESS
    search_monitors = []
    # enforce a time limit (if requested)
    if time_limit:
       search_monitors.append(slv.TimeLimit(time_limit))
    # init search
    slv.NewSearch(decision_builder, search_monitors)

    # SEARCH FOR A FEASIBLE SOLUTION
    sol_found = False
    while slv.NextSolution():
        sol_found = True
        #
        # PRINT SOLUTION
        #
        for i in range(n):
            print ' '.join('%2d' % x[i,j].Value() for j in range(n))
        print
        break

    # END THE SEARCH PROCESS
    slv.EndSearch()

    if not sol_found:
        print '--- No solution found'
        print 

    # obtain stats
    branches, time = slv.Branches(), slv.WallTime()
    # time capping
    time = max(1, time)

    # print stats
    print '--- FINAL STATS'
    print '--- Number of branches: %d' % branches
    print '--- Computation time: %.3f (sec)' % (time / 1000.0)
    if time_limit != None and slv.WallTime() > time_limit:
        print '--- Time limit exceeded'

    # Return the solution value
    return branches, time


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
solve_problem(data, time_limit=20000)