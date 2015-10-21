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

#
# CREATE A SOLVER INSTANCE
# Signature: Solver(<solver name>)
# 
slv = pywrapcp.Solver('timetabling')

# Cache some data for ease of access
rooms = data['rooms']
lectures = data['lectures']
nr = len(data['rooms']) # number of rooms
nl = len(data['lectures']) # number of lectures

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
# Input: a list with the room that was chosen for each lecture
#
def print_sol(room_for_lecture):
    # Loop over each room
    for i, room in enumerate(rooms):
        # Obtain the indices of the lectures in the room
        s = ''
        for j, lecture in enumerate(lectures):
            if room_for_lecture[j] == i:
                s += ' %d' % j
                if lecture['long']:
                    s += '(long)'
        print 'Room #%d: %s' % (i, s)

#
# Search for solutions
#
nsol = 0
while slv.NextSolution():
    print 'SOLUTION FOUND =========================='

    # Find the chosen room for each lecture
    room_for_lecture = # ===== YOUR STUFF HERE =====

    # print solution
    print_sol(room_for_lecture)


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