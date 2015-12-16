#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp
import sys
import json
import math


def filter_max(idx_value_pairs):
    thr = None
    res = []
    for i, v in idx_value_pairs.items():
        if thr is None or v == thr:
            thr = v
            res.append(i)
        elif v > thr:
            thr = v
            res = [i]
    return res


def filter_min(idx_value_pairs):
    thr = None
    res = []
    for i, v in idx_value_pairs.items():
        if thr is None or v == thr:
            thr = v
            res.append(i)
        elif v < thr:
            thr = v
            res = [i]
    return res


def get_domain(var):
    return [j for j in range(var.Min(), var.Max()+1) if var.Contains(j)]


class CustomDecisionBuilder(pywrapcp.PyDecisionBuilder):
  '''
  A dedicated DecisionBuilder for our problem
  '''

  def __init__(self, x, job_dur, srv_cost):
    self.x = x
    self.job_dur = job_dur
    self.srv_cost = srv_cost

  def Next(self, slv):
    # Compute a number of useful pieces of infomation
    # - list of unbound variables
    unbound_idx = []
    for i, var in enumerate(self.x):
        if not var.Bound():
            unbound_idx.append(i)

    # If all variables are bound, then stop search
    if len(unbound_idx) == 0:
        return None

    # Select a variable to branch upon    
    candidates = filter_min({i:self.x[i].Size() for i in unbound_idx})
    sel_var_idx = candidates[0]
    sel_var = self.x[sel_var_idx]

    # Identify the possible values
    values = get_domain(sel_var)

    # Pick the value to be assigned (server with the smallest index)
    sel_val = min(values)

    # Return a Decision object
    return slv.AssignVariableValue(sel_var, sel_val)

#
# A FUNCTION TO BUILD AND SOLVE A MODEL
# time_limit: if None, not time limit is employed. If integer, a time limit is
#             enforced, but optimality is no longer guaranteed!
#
def solve_problem(data, time_limit = None):
    # Cache some useful data
    srv_cost = data['srv_cost']
    job_dur = data['job_dur']

    nsrv = len(srv_cost) # number of server types
    njobs = len(job_dur) # number of jobs
    eoh = max(max(durs) for durs in job_dur) # largest overall duration

    # Build solver instance
    slv = pywrapcp.Solver('production-scheduling')

    # SOME PRE-BUILT VARIABLES
    # One variable for each job
    # Il job x viene eseguito in un server di tipo v
    x = [slv.IntVar(0, nsrv-1, 'x_%d' % i) for i in range(njobs)]

    # A global time variable
    mk = slv.IntVar(0, eoh, 'mk')

    # Cost variable
    z = slv.IntVar(0, sys.maxint, 'z')

    # BUILD THE REST OF THE MODEL HERE (additional variables & constraints)

    # costo c[x[i]]*durata_max
    c_x = [slv.IntVar(min(srv_cost), max(srv_cost), 'c_x_%d' % i) for i in range(njobs)]

    for i, c in enumerate(c_x):
        slv.Add(c == x[i].IndexOf(srv_cost))

    m_x = [slv.IntVar(0, eoh, 'm_x_%d' % i) for i in range(njobs)]
    for i, m in enumerate(m_x):
        slv.Add(m == x[i].IndexOf(job_dur[i]))
    

    slv.Add(mk == slv.Max(m_x))
    slv.Add(z == mk * slv.Sum(c_x))


    # DEFINE THE SEARCH STRATEGY
    db1 = slv.Phase(x, slv.CHOOSE_MIN_SIZE_LOWEST_MIN,
                                    slv.ASSIGN_MAX_VALUE)
    #db1 = CustomDecisionBuilder(x,  job_dur, srv_cost)
    decision_builder = slv.Compose([db1])

    # INIT THE SEARCH PROCESS
    search_monitors = [slv.Minimize(z, 1)]
    if time_limit:
       search_monitors.append(slv.TimeLimit(time_limit))
    # init search
    slv.NewSearch(decision_builder, search_monitors)

    # SEARCH FOR A FEASIBLE SOLUTION
    zbest = None
    while slv.NextSolution():
        #
        # PRINT SOLUTION
        #
        print '--- Solution found, time: %.3f (sec), branches: %d' % \
                    (slv.WallTime()/1000.0, slv.Branches())
        print '--- z: %d' % z.Value()
        print '--- mk: %d' % mk.Value()
        print '--- x:', ', '.join('%3d' % var.Value() for var in x)

        # FEEL FREE TO PRINT MORE STUFF, IF YOU WISH TO

        # STORE SOLUTION VALUE
        zbest = z.Value()

    # END THE SEARCH PROCESS
    slv.EndSearch()

    # obtain stats
    branches, time = slv.Branches(), slv.WallTime()
    # time capping
    time = max(1, time)

    # print stats
    print '--- FINAL STATS'
    if zbest == None:
        print '--- No solution found'
    print '--- Number of branches: %d' % branches
    print '--- Computation time: %.3f (sec)' % (time / 1000.0)
    if time_limit != None and time > time_limit:
        print '--- Time limit exceeded'

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
solve_problem(data, time_limit=20000)