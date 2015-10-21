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
The Norwegian lives next to the blu house.

Who owns a zebra and who drinks water?

Persone: [inglese, spagnolo, ucraino, norvegese, giapponese]

Case: [rossa, verde, gialla, blu, avorio]

Animali: [cane, lumaca, volpe, zebra, cavallo]

Drinks: [acqua, caffe corretto, tea, latte corretto, aranciata]

Sigarette: [Old Gold, Chesterfields, Lucky Strike, Parilaments, Kools]

"""

# LE VARIABILI DA USARE SONO L'INDIRIZZO DELLA CASA! NON LA CASA!

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

houses = {
    'rossa':0, 
    'verde':1, 
    'gialla':2,
    'blu':3,
    'avorio':4
}

people = {
    'inglese':0,
    'spagnolo':1,
    'ucraino':2,
    'norvegese':3,
    'giapponese':4
}

animals = {
    'cane':0,
    'lumache':1,
    'volpe':2,
    'zebra':3,
    'cavallo':4
}

drinks = {
    'acqua':0,
    'caffe':1, 
    'te':2, 
    'latte':3, 
    'aranciata':4
}

smokes = {
    'Old Gold':0, 
    'Chesterfields':1, 
    'Lucky Strike':2, 
    'Parliaments':3, 
    'Kools':4
}

# ogni casa puo' essere di una persona

# Variabili
# person_i = x --> la persona vive nella casa di indirizzo X
# animal_i = x --> l'animale vive nella casa di indirizzo X
# ecc.

addresses = range(5) # l'indirizzo di una casa

people_vars = [slv.IntVar(addresses, 'n%d' % i) for i in addresses]
animal_vars = [slv.IntVar(addresses, 'a%d' % i) for i in addresses]
house_vars = [slv.IntVar(addresses, 'c%d' % i) for i in addresses]
drink_vars = [slv.IntVar(addresses, 'd%d' % i) for i in addresses]
smoke_vars = [slv.IntVar(addresses, 's%d' % i) for i in addresses]



#
# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
# Signature: Add(<constraint>)
#

# Vincoli del tipo:
# la persona i non può essere nella stessa casa della persona j
# l'animale i non può essere nella stessa casa dell'animale j
# ...

for i in range(0, len(houses)):
    for j in range(i+1,len(houses)):
        slv.Add(people_vars[i] != people_vars[j])
        slv.Add(animal_vars[i] != animal_vars[j])
        slv.Add(drink_vars[i] != drink_vars[j])
        slv.Add(smoke_vars[i] != smoke_vars[j])
        slv.Add(house_vars[i] != house_vars[j])



# Vincolo l'inglese sta nella casa rossa
slv.Add(people_vars[people['inglese']] == house_vars[houses['rossa']])

#people_vars[people['inglese']].SetValues([houses['rossa']])

# Vincolo caffe nella casa vede
slv.Add(drink_vars[drinks['caffe']] == house_vars[houses['verde']])

# Vincolo spagnolo in casa con il cane
slv.Add(people_vars[people['spagnolo']] == animal_vars[animals['cane']])

# Vincolo ucraino - te
slv.Add(people_vars[people['ucraino']] == drink_vars[drinks['te']])

# Vincolo casa verde a destra della casa avorio (indirizzo più grande)
# Non serve un bound check perché le variabili sono limitate
slv.Add(house_vars[houses['verde']] == (house_vars[houses['avorio']] + 1)) 

# Vincolo Old Gold - snails
slv.Add(smoke_vars[smokes['Old Gold']] == animal_vars[animals['lumache']])

# Vincolo Kools - casa gialla
slv.Add(smoke_vars[smokes['Kools']] == house_vars[houses['gialla']])

# Vincolo Milk - casa di mezzo
slv.Add(drink_vars[drinks['latte']] == len(house_vars)/2) # Divisione tra interi -> ritorna 2

# Vincolo Norvegese in prima casa
slv.Add(people_vars[people['norvegese']] == 0)

# Vincolo Chester - Vicino alla casa della volpe
# Non serve un bound check perché le variabili sono limitate
slv.Add(abs(smoke_vars[smokes['Chesterfields']] - animal_vars[animals['volpe']]) == 1)

# Vincolo Kools - Vicino alla casa della cavallo
# Non serve un bound check perché le variabili sono limitate
slv.Add(abs(smoke_vars[smokes['Kools']] -(animal_vars[animals['cavallo']])) == 1)

# Vincolo aranciata - lucky strikes
slv.Add(smoke_vars[smokes['Lucky Strike']] == drink_vars[drinks['aranciata']])

# Vincolo Giapponese Parliaments
slv.Add(people_vars[people['giapponese']] == smoke_vars[smokes['Parliaments']])

# Vincolo Norvegese vicino alla casa blu
# Cioè l'indirizzo della casa del norvegese è +-1 rispetto a quello della casa blu
# In teoria può essere semplificato perché il norvegese ha il vincolo che è nella prima casa (un solo vicino)

slv.Add(abs(people_vars[people['norvegese']] - house_vars[houses['blu']])== 1)


#
# THOSE ARE THE VARIABLES THAT WE WANT TO USE FOR BRANCHING
#
all_vars = people_vars + animal_vars + drink_vars + smoke_vars + house_vars

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

    print people_vars

    print 'Water is drinked in house %d' % drink_vars[drinks['acqua']].Value()
    print 'The zebra is in house %d' % animal_vars[animals['zebra']].Value()


    # WE WANT A SINGLE SOLUTION
    nsol += 1

if nsol == 0:
    print 'no solution found'
print nsol
#
# END THE SEARCH PROCESS
#
slv.EndSearch()
