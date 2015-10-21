#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp


#
# To access system variables
#
import sys

#
# For parsing JSON data
#
import json

#
# Parse command line
#
if len(sys.argv) != 2:
    print 'Usage: python %s <data file>' % sys.argv[0]
    sys.exit()
else:
    fname = sys.argv[1]

#
# READ PROBLEM DATA
#
with open(fname) as fin:
    data = json.load(fin)

# For simplicity: coordinates of the 3x3 boxes

boxes  = [
    [(0,0), (0,1), (0,2),
     (1,0), (1,1), (1,2),
     (2,0), (2,1), (2,2)],
    [(0,3), (0,4), (0,5),
     (1,3), (1,4), (1,5),
     (2,3), (2,4), (2,5)],
    [(0,6), (0,7), (0,8),
     (1,6), (1,7), (1,8),
     (2,6), (2,7), (2,8)],

    [(3,0), (3,1), (3,2),
     (4,0), (4,1), (4,2),
     (5,0), (5,1), (5,2)],
    [(3,3), (3,4), (3,5),
     (4,3), (4,4), (4,5),
     (5,3), (5,4), (5,5)],
    [(3,6), (3,7), (3,8),
     (4,6), (4,7), (4,8),
     (5,6), (5,7), (5,8)],

    [(6,0), (6,1), (6,2),
     (7,0), (7,1), (7,2),
     (8,0), (8,1), (8,2)],
    [(6,3), (6,4), (6,5),
     (7,3), (7,4), (7,5),
     (8,3), (8,4), (8,5)],
    [(6,6), (6,7), (6,8),
     (7,6), (7,7), (7,8),
     (8,6), (8,7), (8,8)]
]


#
# CREATE A SOLVER INSTANCE
# Signature: Solver(<solver name>)
# 
slv = pywrapcp.Solver('sudoku')

# Cache some data for ease of access
grid = data['grid']
n = 9


#
# CREATE VARIABLES
# Signature: IntVar(<min>, <max>, <name>)
#

# ===== YOUR STUFF HERE =====

#
# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
# Signature: Add(<constraint>)
#

# ===== YOUR STUFF HERE =====

#
# THOSE ARE THE VARIABLES THAT WE WANT TO USE FOR BRANCHING
#

# we need to flatten the dictionary here
all_vars = # ===== YOUR STUFF HERE =====

#
# DEFINE THE SEARCH STRATEGY
# we will keep this fixed for a few more lectures
#
decision_builder = slv.Phase(all_vars,
                                slv.INT_VAR_DEFAULT,
                                slv.INT_VALUE_DEFAULT)

#
# INIT THE SEARCH PROCESS
# we will keep this fixed for a few more lectures
#
time_limit = 20000
search_monitors = [slv.SearchLog(500000), slv.TimeLimit(time_limit)]
slv.NewSearch(decision_builder, search_monitors)

#
# Function to print a solution
# Input format: dictionary with tuple keys (i,j). The (i,j) element is the
# number in the i,j cell
#
def print_sol(cell_content):
    for i in range(n):
        print ' '.join('%d' % cell_content[i,j] for j in range(n))

#
# Search for a solution
#
nsol = 0
while slv.NextSolution():
    print 'SOLUTION FOUND =========================='

    # Obtain the content of each cell in a dictionary
    cell_content = # ===== YOUR STUFF HERE =====

    # print the solution
    print_sol(cell_content)

    print 'END OF SOLUTION =========================='

    # WE WANT A SINGLE SOLUTION
    nsol += 1
    break

#
# END THE SEARCH PROCESS
#
slv.EndSearch()

if nsol == 0:
    print 'no solution found'

# Print solution information
print 'Number of branches: %d' % slv.Branches()
print 'Number of fails: %d' % slv.Failures()
print 'Computation time: %f (ms)' % slv.WallTime()
if slv.WallTime() > time_limit:
    print 'Time limit exceeded'