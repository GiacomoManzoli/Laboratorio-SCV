
from ortools.constraint_solver import pywrapcp


import sys
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
slv = pywrapcp.Solver('tanks')

# Cache some data for ease of access
tanks = data['tanks']
chemicals = data['chemicals']
nt = len(tanks)
nc = len(chemicals)

#
# CREATE VARIABLES
# Signature: IntVar(<min>, <max>, <name>)
#
# C'è una certa quantità di ogni sostanza chimica
# Ogni tank può contenere una singola sostanza
# Ogni tank ha una determinata capacità che non può essere superata
# Alcune sostenze chimiche sono pericolose e devono essere immagazzinate
#   in taniche particolari
# Ogni sostanza chimica deve essere tenuta ad una certa temperatura
#   - Se tmax_i < tmin_j o tmax_j < tmin_i le due sostanze non possono essere vicine


# chemical_vars[i] = j --> Metto la sostanza i nel container j
chemical_vars = []
for chemical in chemicals:
    chemical_vars.append(slv.IntVar(range(0,nt), "Sostanza"+str(len(chemical_vars))))

#
# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
# Signature: Add(<constraint>)
#

# Vincoli una sola sostanza per container
for i in range(0, len(chemical_vars)):
    for j in range(i+1, len(chemical_vars)):
        slv.Add(chemical_vars[i] != chemical_vars[j])


for i in range(0,len(chemical_vars)):
    for j in range(0, len(tanks)):
        # Vincoli sulla capacità per la variabile i
        #   Se non ci sta aggiungo il vincolo che sia diverso
        if chemicals[i]['amount'] > tanks[j]['cap']:
            slv.Add(chemical_vars[i] != j)
        # Vincolo sulla sicurezza
        # Se il nontenitore non è sicuro e la sostanza è pericolosa aggiungo il vincolo del diverso
        if not(tanks[j]['safe']) and chemicals[i]['dangerous']:
            slv.Add(chemical_vars[i] != j)


# Vincolo sulla termperatura
for i in range(0,len(chemical_vars)):
    for j in range(i+1, len(chemical_vars)):
        if chemicals[i]['tmax'] < chemicals[j]['tmin'] or chemicals[i]['tmin'] > chemicals[j]['tmax']:
            slv.Add(abs(chemical_vars[i] - chemical_vars[j]) != 1)


#
# THOSE ARE THE VARIABLES THAT WE WANT TO USE FOR BRANCHING
#
all_vars = chemical_vars

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
# Input format: list with the tank index chosen for each chemical
#
def print_sol(tank_for_chemical):
    # Obtain and transform the solution data
    cap = ['%5d' % t['cap'] for t in tanks]
    idx = [' --- ' for i in range(nt)] # chemical index in ech tank
    amt = [' --- ' for i in range(nt)] # chemical amount in each tank
    tmin = [' --- ' for i in range(nt)] # chemical tmin in each tank
    tmax = [' --- ' for i in range(nt)] # chemical tmax in each tank
    for i in range(nt):
        for j in range(nc):
            if tank_for_chemical[j] == i:
                idx[i] = '%5d' % j
                amt[i] = '%5d' % chemicals[j]['amount']
                tmin[i] = '%5d' % chemicals[j]['tmin']
                tmax[i] = '%5d' % chemicals[j]['tmax']

    print 'CHEMICALS : %s' % ', '.join(idx)
    print 'CAPACITIES: %s' % ', '.join(cap)
    print 'AMOUNTS   : %s' % ', '.join(amt)
    print 'TMIN      : %s' % ', '.join(tmin)
    print 'TMAX      : %s' % ', '.join(tmax)

#
# Search for a solution
#
nsol = 0
while slv.NextSolution():
    print 'SOLUTION FOUND =========================='

    # Obtain the chosen tank for each chemical

    tank_for_chemical = []
    for var in all_vars:
        tank_for_chemical.append(int(var.Value()))
    
    #print tank_for_chemical
    # print the solution
    
    print tank_for_chemical

    print_sol(tank_for_chemical)

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
print 'Computation time: %f (ms)' % slv.WallTime()
if slv.WallTime() > time_limit:
    print 'Time limit exceeded'