"""
Model & Solve the zebra problem as invented by Lewis Caroll:

There are five houses.
The Englishman lives in the red house.
The Spaniard owns the dog.
Coffee is drunk in the green house.
The Ukrainian drinks tea.
The green house is immediately to the right of the ivory house.
The Old Gold smoker owns snails.
Kools are smoked in the yellow house.
Milk is drunk in the middle house.
The Norwegian lives in the first house.
The man who smokes Chesterfields lives in the house next to the man
   with the fox.
Kools are smoked in the house next to the house where the horse is kept.
The Lucky Strike smoker drinks orange juice.
The Japanese smokes Parliaments.
The Norwegian lives next to the blue house.

Who owns a zebra and who drinks water?

Persone: [inglese, spagnolo, ucraino, norvegese, giapponese]

Case: [rossa, verde, gialla, blue, avorio]

Animali: [cane, lumaca, volpe, zebra, cavallo]

Drinks: [acqua, caffe corretto, tea, latte corretto, aranciata]

Sigarette: [Old Gold, Chesterfields, LuckyStrike, Parilaments, Kools]

"""

#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp

#
# CREATE A SOLVER INSTANCE
# Signature: Solver(<solver name>)
# 
#
slv = pywrapcp.Solver('map-coloring')

#
# CREATE VARIABLES
# Signature: IntVar(<min>, <max>, <name>)
#

people = ['inglese', 'spagnolo', 'ucraino', 'norvegese', 'giapponese']
houses = ['rossa', 'verde', 'gialla', 'blue', 'avorio']
animals = ['cane', 'lumaca', 'volpe', 'zebra', 'cavallo']
drinks = ['acqua', 'caffe corretto', 'tea', 'latte corretto', 'aranciata']
smokes = ['Old Gold', 'Chesterfields', 'LuckyStrike', 'Parilaments', 'Kools']


# ogni casa puo' essere di una persona
house_vars = []
for house in houses:
    house_vars.append(slv.IntVar(0, len(houses)-1, house))

animal_vars = []
for animal in animals:
    animal_vars.append(slv.IntVar(0, len(animals)-1, animal)) 

drink_vars = []
for drink in drinks:
    drink_vars.append(slv.IntVar(0, len(drinks)-1, drink))

smoke_vars = []
for smoke in smokes:
    smoke_vars.append(slv.IntVar(0, len(smokes)-1, smoke)) 

#
# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
# Signature: Add(<constraint>)
#

# la stessa persona puo' avere una sola casa

for (h1, h2) in zip(house_vars,house_vars):
    if h1 != h2:
        slv.add(h1 != h2)

# la stessa persona puo' avere un solo animale

for (h1, h2) in zip(animal_vars,animal_vars):
    if h1 != h2:
        slv.add(h1 != h2)

# la stessa persona puo' avere un solo drink

for (h1, h2) in zip(drink_vars,drink_vars):
    if h1 != h2:
        slv.add(h1 != h2)

# la stessa persona puo' avere una sola marca di sigarette

for (h1, h2) in zip(smoke_vars,smoke_vars):
    if h1 != h2:
        slv.add(h1 != h2)

# ------- DO THIS YOURSELVES! -------


#
# THOSE ARE THE VARIABLES THAT WE WANT TO USE FOR BRANCHING
#
all_vars = # ------- DO THIS YOURSELVES! -------

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
slv.NewSearch(decision_builder)

#
# Enumerate all solutions!
#
nsol = 0
while slv.NextSolution():
    # Here, a solution has just been found. Hence, all variables are bound
    # and their "Value()" method can be called without errors.
    # The notation %2d prints an integer using always two "spaces"

    # ------- DO THIS YOURSELVES! -------

    # WE WANT A SINGLE SOLUTION
    nsol += 1
    break

if nsol == 0:
    print 'no solution found'

#
# END THE SEARCH PROCESS
#
slv.EndSearch()
