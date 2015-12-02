#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp
import sys
import json
import math

# BRANCH AND BOUND
def branch_and_bound(solve_function, data,
                     time_limit = None):
    print
    print '==================================================' 
    print 'Solving the problem via branch & bound'
    #print '=================================================='
    #print
    zbest, branches, time = solve_function(data, time_limit)
    #print
    #print '==================================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'NO SOLUTION FOUND'
    print '- total number of branches: %d' % branches
    print '- total time (sec): %.3f' % (time / 1000.0)
    if time_limit != None and time >= time_limit:
        print '- TIME LIMIT EXCEEDED'
    print '==================================================' 


# DESTRUCTIVE LOWER BOUNDING
def destructive_lb(solve_function, data, start, time_limit = None):
    print
    print '==================================================' 
    print 'Solving the problem via destructive lower bounding'
    print '=================================================='
    print
    zbest = None
    branches, time = 0, 0
    while zbest == None:
        print
        print '--------------------------------------------------' 
        print 'Checking value %d for feasibility' % start
        print
        if time_limit != None: time_limit - time
        zbest, br, tm = solve_function(data, ub = start,
                                       time_limit = time_limit)
        branches += br
        time += tm
        if zbest == None:
            start += 1
    print
    print '==================================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'NO SOLUTION FOUND'
    print '- total number of branches: %d' % branches
    print '- total time (sec): %.3f' % (time / 1000.0)
    if time_limit != None and time >= time_limit:
        print '- TIME LIMIT EXCEEDED'
    print '==================================================' 


# DESTRUCTIVE UPPER BOUNDING
def destructive_ub(solve_function, data, start, time_limit = None):
    print
    print '==================================================' 
    print 'Solving the problem via destructive upper bounding'
    print '=================================================='
    print
    zbest = start
    last_z = zbest
    branches, time = 0, 0
    while last_z != None:
        print
        print '--------------------------------------------------' 
        print 'Searching for a solution within cost %d' % start
        print
        if time_limit != None: time_limit - time
        last_z, br, tm = solve_function(data, ub = start,
                                        time_limit = time_limit)
        branches += br
        time += tm
        if last_z != None:
            zbest = last_z
            start = zbest - 1
    print 
    print '==================================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
    else:
        print 'NO SOLUTION FOUND'
    print '- total number of branches: %d' % branches
    print '- total time (sec): %.3f' % (time / 1000.0)
    if time_limit != None and time >= time_limit:
        print '- TIME LIMIT EXCEEDED'
    print '==================================================' 


# BINARY SEARCH
def binary_search(solve_function, data, start_lb, start_ub, time_limit = None):
    print
    print '==================================================' 
    print 'Solving the problem via binary search'
    print '=================================================='
    print
    zbest = start_ub
    branches, time = 0, 0
    cnt = 0
    while zbest > start_lb+1:
        theta = (start_lb + start_ub) / 2
        print
        print '--------------------------------------------------' 
        print 'Searching for a solution with cost in [%d..%d]' % (start_lb, theta)
        print

        if cnt > 3: sys.exit()

        if time_limit != None: time_limit - time
        last_z, br, tm = solve_function(data, lb = start_lb+1, ub = theta,
                                        time_limit = time_limit)
        branches += br
        time += tm
        if last_z != None:
            zbest = last_z
            start_ub = zbest
        else:
            if time_limit != None and time > time_limit:
                break
            else:
                start_lb = theta

        cnt += 1
    print 
    print '==================================================' 
    if zbest != None:
        print 'THE FINAL SOLUTION VALUE IS: %d' % zbest
        print '- best lower bound: %d' % start_lb
    else:
        print 'NO SOLUTION FOUND'
    print '- total number of branches: %d' % branches
    print '- total time (sec): %.3f' % (time / 1000.0)
    if time_limit != None and time >= time_limit:
        print '- TIME LIMIT EXCEEDED'
    print '==================================================' 

#
# A FUNCTION TO BUILD AND SOLVE A MODEL
# time_limit: if None, not time limit is employed. If integer, a time limit is
#             enforced, but optimality is no longer guaranteed!
# lb:         if not None, search for a solution with cost >= lb
# ub:         if not None, search for a solution with cost <= lb
#
def solve_problem(data, time_limit = None, lb = None, ub = None):
    # Cache some useful data
    services = data['services']
    nservices = len(services)
    nservers = data['nservers']
    cap_cpu = data['cap_cpu']

    # split services into individual VMs
    vm_svc = [] # service idx, for each VM
    vm_cpu = [] # CPU requirement, for each VM
    for k, svc in enumerate(services):
        vm_num = svc['vm_num']
        vm_svc += [k] * vm_num
        vm_cpu += [svc['vm_cpu']] * vm_num

    nvm = len(vm_svc)


    # Build solver instance
    slv = pywrapcp.Solver('production-scheduling')

    # Cost variable (number of used services)
    
    z = slv.IntVar(0, nservers, 'z')

    # One variable for each VM, specifica che server esegue la vm
    x = [slv.IntVar(0, nservers-1, 'x_%d' % i) for i in range(nvm)]

    # VMs within the same service should go on different servers
    for i in range(nvm):
        for j in range(i+1, nvm):
            if vm_svc[i] == vm_svc[j]:
                #slv.Add(x[i] != x[j])
                slv.Add(x[i] < x[j])

    #for s in range(nservices):
    #    vm_s = [x[i] for i in range(nvm) if vm_svc[i] == s]
    #    print vm_s
    #    slv.Add(slv.AllDifferent(vm_s, True))

    # Taglio un po' di simmetrie, la prima vm sta nel primo server
    slv.Add(x[0] == 0)

    # Devo avere almeno tanti server quante vm ha il servizio piu' grosso
    min_server = nservers
    for i in range(len(services)):
        if services[i]['vm_num'] < min_server:
            min_server = services[i]['vm_num']
    slv.Add(z >= min_server)

    # Due Vm che richiedono piu' di meta' devono essere su server diversi
    half_cap = cap_cpu/2
    over_cap = [x[i] for i in range(nvm) if vm_cpu[i] > half_cap]
    for i in range(len(over_cap)):
        for j in range(i+1,len(over_cap)):
            slv.Add(x[i] < x[j])

    # CPU capacity constraints
    for j in range(nservers):
        # Obtain an expression for the total CPU requirement
        cpu_cnt = sum(v * (x[i] == j) for i, v in enumerate(vm_cpu))
        # Post CPU capacity constraint
        slv.Add(cpu_cnt <= cap_cpu)

    # Cost definition (exploits value symmetry)
    slv.Add(z == 1 + slv.Max(x))

    # Bounding constraints
    if lb != None:
        slv.Add(z >= lb)
    if ub != None:
        slv.Add(z <= ub)

    # DEFINE THE SEARCH STRATEGY
    decision_builder = slv.Phase(x,
                                 slv.CHOOSE_MIN_SIZE_LOWEST_MIN,
                                 slv.ASSIGN_MIN_VALUE)

    # INIT THE SEARCH PROCESS
    search_monitors = []
    if lb == None and ub == None:
        search_monitors.append(slv.Minimize(z, 1))
    # enforce a time limit (if requested)
    if time_limit:
       search_monitors.append(slv.TimeLimit(time_limit))
    # init search
    slv.NewSearch(decision_builder, search_monitors)

    #print 'vm_svc:', vm_svc
    #print 'vm_cpu:', vm_cpu

    # SEARCH FOR A FEASIBLE SOLUTION
    zbest = None
    while slv.NextSolution():
        #
        # PRINT SOLUTION
        #
        #print '--- Solution found, time: %.3f (sec), branches: %d' % \
        #            (slv.WallTime()/1000.0, slv.Branches())
        #print '--- z: %d' % z.Value()
        #print '--- x:', ', '.join('%3d' % var.Value() for var in x)

        cpu_req = [sum(v for i, v in enumerate(vm_cpu) if x[i].Value() == j)
                    for j in range(nservers)]
        #print '--- cpu:', ', '.join('%3d' % v for v in cpu_req)
        #print

        # STORE SOLUTION VALUE
        zbest = z.Value()
        # stop search if not using B&B
        if lb != None or ub != None: break

    # END THE SEARCH PROCESS
    slv.EndSearch()

    # obtain stats
    branches, time = slv.Branches(), slv.WallTime()
    # time capping
    time = max(1, time)

    # print stats
    #print '--- FINAL STATS'
    #if zbest == None:
    #    print '--- No solution found'
    #print '--- Number of branches: %d' % branches
    #print '--- Computation time: %.3f (sec)' % (time / 1000.0)
    #if time_limit != None and slv.WallTime() > time_limit:
    #    print '--- Time limit exceeded'

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
branch_and_bound(solve_problem, data, time_limit=15000)

# smin = min(svc['vm_num'] for svc in data['services'])
# smax = data['nservers']
# binary_search(solve_problem, data,
#               start_lb = smin, start_ub = smax, time_limit = 15000)