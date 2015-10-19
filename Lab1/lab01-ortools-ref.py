#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp

#
# CREATE A SOLVER INSTANCE
# Signature: Solver(<solver name>)
# 
#
slv = pywrapcp.Solver('simple-example')

#
# CREATE VARIABLES
# Signature: IntVar(<min>, <max>, [<name>])
# Alternative signature: IntVar(<domain as a list>, [<name>])
#
x1 = slv.IntVar(-2, 2, 'x1')
x2 = slv.IntVar(-2, 2, 'x2')
x3 = slv.IntVar(-2, 2, 'x3')

#
# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
# Signature: Add(<constraint>)
#
slv.Add(x3 == x1 + x2)

#
# DEFINE THE SEARCH STRATEGY
# we will keep this fixed for a few more lectures
#
all_vars = [x1, x2, x3]
decision_builder = slv.Phase(all_vars,
                                slv.INT_VAR_DEFAULT,
                                slv.INT_VALUE_DEFAULT)

#
# INIT THE SEARCH PROCESS
# we will keep this fixed for a few more lectures
#
slv.NewSearch(decision_builder)

#
# Enumerate all solutions!
#
while slv.NextSolution():
    # Here, a solution has just been found. Hence, all variables are bound
    # and their "Value()" method can be called without errors.
    # The notation %2d prints an integer using always two "spaces"
    print 'x1: %2d, x2: %2d, x3: %2d' % (x1.Value(), x2.Value(), x3.Value())

#
# END THE SEARCH PROCESS
#
slv.EndSearch()