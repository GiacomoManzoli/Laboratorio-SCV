
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
slv = pywrapcp.Solver('timetabling')

# Cache some data for ease of access
rooms = data['rooms']
lectures = data['lectures']
nr = len(data['rooms']) # number of rooms
nl = len(data['lectures']) # number of lectures


# Ci sono NR stanze e devo fare NL lezioni
# Ogni lezione ha un certo numero di partecipanti e per quella data lezione l'aula deve essere sufficentemente grande

#
# CREATE VARIABLES
# Signature: IntVar(<min>, <max>, <name>)
#

lecture_room_vars = []
# lecture_room_i = x : la lezione i si tiene nell'aula x.

for i in range(nl):
    lecture_room_vars.append(slv.IntVar(range(nr), 'Aula Lezione %d'%i))

lecture_turn_vars = []
# lecture_turn_i = x : la lezione si tiene al turno x

for i in range(nl):
    lecture_turn_vars.append(slv.IntVar(range(2), 'Turno Lezione %d'%i)) # Massimo 2 turni

#
# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
# Signature: Add(<constraint>)
#

# Vincolo sulla capacità 
for i in range(nl):
    for j in range(nr):
        if lectures[i]['num'] > rooms[j]['cap']:
            slv.Add(lecture_room_vars[i] != j)

# Se due lezioni si tengono sulla stessa aula i turni devono essere diversi
for i in range(nl):
    for j in range(nl):
        if i != j:
            # -abs(t1 - t2) == 0 se i turni sono uguali, -1 se i turni sono diversi
            # abs(r1 - r2) == 0 se la stanza è la stessa, >0 altrimenti. 
            # r1 - r2 > t1 - t2 = True : SE t1 - t2 = 0 Allora r1-r2 > 0 --> a turni uguali la differenza tra le due stanze deve essere >0, non possono esserci due stanze uguali nello stesso turno.
            #                            SE t1- t2 = -1 allora r1-t2 > -1 --> a turni diversi la differenza tra le stanze deve essere >= 0.
            #                   = False : Se t1 - t2 = 0 Allora r1-r2 = 0 --> a turni uguali ci sono due stanze uguali, è giusto False
            #                           : Se t1 - t2 = -1 allora r1-r2 <= -1 ma r1-r2 è sempre maggiore di 0, quindi non può mai verificarsi come situazione
            slv.Add( abs(lecture_room_vars[i] - lecture_room_vars[j]) > (-1*abs(lecture_turn_vars[i] - lecture_turn_vars[j])) )

# Se la lezione è lunga la lezione deve tenersi al primo turno e l'aula non può più essere usata
for i in range(nl):
    if lectures[i]['long']:
       # La lezione deve essere tenuta al primo turno
       slv.Add(lecture_turn_vars[i] == 0)
       for j in range(nl):
            if i != j:
                slv.Add(lecture_room_vars[i] != lecture_room_vars[j])



# Se la lezione è corta l'aula compare al massimo due volte due volte


#
# THOSE ARE THE VARIABLES THAT WE WANT TO USE FOR BRANCHING
#

# we need to flatten the dictionary here
all_vars = lecture_room_vars + lecture_turn_vars

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

    #room_for_lecture =

    # print solution
    #print_sol(room_for_lecture)
    print '           | Aula | Turno'
    for i in range(nl):
        d =''
        if lectures[i]['long']:
            d = '(long)'
        print 'Lezione %d: %d - %d %s' % (i , lecture_room_vars[i].Value() , lecture_turn_vars[i].Value(), d)

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