#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def filter_by_idx(values, idx):
    return [values[i] for i in idx]


def get_domain(var):
    return [j for j in range(var.Min(), var.Max()+1) if var.Contains(j)]
 #

class MaxRequestFirstDecisionBuilder(pywrapcp.PyDecisionBuilder):
  '''
  A dedicated DecisionBuilder for our problem
  '''
  def __init__(self, x, req,vm_svc, svc_vm, cap, nservers):
    self.x = x
    self.req = req
    self.vm_svc = vm_svc    # vm_svc[i] = k --> la vm i si è del service k
    self.svc_vm = svc_vm    # svc_vm[k] = n --> il service k ha n vm
    self.cap = cap
    self.nservers = nservers
    self.MAX_VALUE = 1000

  def Next(self, slv):
    # Compute a number of useful pieces of infomation
    # - load on each server
    # - list of unbound variables
    load = [0 for j in range(self.nservers)]
    unbound_idx = []
    for i, var in enumerate(self.x):
        if var.Bound():
            load[var.Value()] += self.req[i]
        else:
            unbound_idx.append(i)

    # If all variables are bound, then stop search
    if len(unbound_idx) == 0:
        return None

    # Scelgo tra le variabili che hanno maggior richieste di CPU
    candidates = filter_max({i:self.req[i] for i in unbound_idx})
    # Tra quelle che hanno la maggior richiesta, prendo quelle che hanno il maggiorn numero di vm
    candidates = filter_max({i: self.svc_vm[self.vm_svc[i]] for i in candidates})

    sel_var_idx = candidates[0]
    sel_var = self.x[sel_var_idx]

    # Controllo se ho già fatto delle assegnazioni
    if len(unbound_idx) == len(self.req):
        # Non sono ancora state assegnati dei valori
        return slv.AssignVariableValueOrFail(sel_var, 0) # un server vale l'altro

        ## trova il service della VM
        ## sel_var_idx è l'indice della prima VM del service (perché è il primo assegnamento)
        #service = self.vm_svc[sel_var_idx]
        ## seleziona tutte le Vm del service
        #vms = [self.x[i] for i in range(sel_var_idx, sel_var_idx+self.svc_vm[service])]
        #vals = [i for i in range(len(vms))]
        #
        ## esegue l'assegnamento in blocco
        #if len(vms) > nservers:
        #    return None # problema infeasible
        #else:
        #    # MakeAssignVariablesValues (const IntVar *const *vars, int size, const int64 *const values)
        #    return slv.AssignVariablesValues(vms, len(vms),vals)

    else:
        # Identify the possible values
        values = get_domain(sel_var) # lista di interi
        
        # Viene messa sul primo server best-fit
        vm_idx = sel_var_idx
        vm_request = self.req[vm_idx]

        excess = []
        for server in values:
            exc = self.cap - (load[server] + vm_request)
            if (exc >= 0):
                excess.append(exc)
            else:
                excess.append(self.MAX_VALUE) # valore farlocco, prendo il minimo eccesso
        
        values_indexs = filter_min({i:e for i,e in enumerate(excess)})
        sel_val_idx = values_indexs[0]
        sel_val = values[sel_val_idx]
        # se il server a cui assegnare la variabile è vuoto, faccio probing
        if load[sel_val] == 0:
            # sel_val == min(values)
            #print 'probe'
            return slv.AssignVariableValueOrFail(sel_var, sel_val)
        else:
            return slv.AssignVariableValue(sel_var, sel_val)

#
# A FUNCTION TO BUILD AND SOLVE A MODEL
# time_limit: if None, not time limit is employed. If integer, a time limit is
#             enforced, but optimality is no longer guaranteed!
#
def solve_problem(data, time_limit = None):
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

    # da sistemare
    svc_vm = [] # VM_num per ogni service
    for i,svc in enumerate(services):
        svc_vm.append(services[i]['vm_num'])    


    # Build solver instance
    slv = pywrapcp.Solver('production-scheduling')

    # Cost variable (number of used services)
    z = slv.IntVar(0, nservers, 'z')

    # One variable for each VM
    x = [slv.IntVar(0, nservers-1, 'x_%d' % i) for i in range(nvm)]

    # VMs within the same service should go on different servers (this is
    # enforced via an AllDifferent global constraint)
    for k in range(nservices):
        slv.Add(slv.AllDifferent([x[i] for i, svc in enumerate(vm_svc) if svc == k]))


    # Symmetry breaking:
    # - All VMs within a service are identical
    # - The corresponding variables must be all differnt
    # Hence, symmetries can be enforced via the lex-leader method by forcing
    # the variale to follow a pre-specified order
    for i in range(nvm-1):
        if vm_svc[i] == vm_svc[i+1]:
            slv.Add(x[i] < x[i+1])

    # CPU capacity constraints
    for j in range(nservers):
        # Obtain an expression for the total CPU requirement
        cpu_cnt = sum(v * (x[i] == j) for i, v in enumerate(vm_cpu))
        # Post CPU capacity constraint
        slv.Add(cpu_cnt <= cap_cpu)

    # Cost definition (exploits a dominance rule)
    slv.Add(z == 1 + slv.Max(x))

    # DEFINE THE SEARCH STRATEGY
    decision_builder = MaxRequestFirstDecisionBuilder(x, vm_cpu, vm_svc, svc_vm, cap_cpu, nservers)

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
        print '--- x:', ', '.join('%3d' % var.Value() for var in x)

        cpu_req = [sum(v for i, v in enumerate(vm_cpu) if x[i].Value() == j)
                    for j in range(nservers)]
        print '--- cpu:', ', '.join('%3d' % v for v in cpu_req)
        print

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