#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import *

def binary_ne_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only binary all-different
    constraints for both the row and column constraints.

    Returns a CSP object representing a FunPuzz Grid CSP problem along with an array of variables
    for the problem. That is return:

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using binary constraints
    to enforce row and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """


    boardSize = funpuzz_grid[0][0]
    basicDomain = []
    for i in range(boardSize):
        basicDomain.append(i+1)

    boardVars = []
    rowOrganized = []
    colOrganized = []

    #set basic domain variables for all squares (left to right then up to down)
    for y in range(boardSize):
        newRow = []
        colOrganized.append([])
        for x in range(boardSize):
            varName = str(x+1) + str(y+1)
            var = Variable(varName, basicDomain)
            newRow.append(var)
        rowOrganized.append(newRow)

    for x in range(boardSize):
        for y in range(boardSize):
            colOrganized[y].append(rowOrganized[x][y])

    for y in range(boardSize):
        for x in range(boardSize):
            boardVars.append(rowOrganized[y][x])


    # boardVars is filled with 11, 21, 31, ... 12, 22, 32, etc

    # Now, we have to handle constraints
    # So, the constraints will be the same for basically all variables and we can precalculate all of the permutations
    # that are valid for any square
    possibleCombos = list(permutations(basicDomain, 2))

    binCSP = CSP("BinaryNoCageCSP", boardVars)
    for row in rowOrganized:
        for v in row:
            for w in row:
                if not w is v:
                    consName = "RowBinConstraint" + v.name
                    newRowCons = Constraint(consName, [v, w])
                    newRowCons.add_satisfying_tuples(possibleCombos)
                    binCSP.add_constraint(newRowCons)


    for col in colOrganized:
        for v in col:
            for w in col:
                if not w is v:
                    consName = "ColBinConstraint" + v.name
                    newColCons = Constraint(consName, [v, w])
                    newColCons.add_satisfying_tuples(possibleCombos)
                    binCSP.add_constraint(newColCons)


    return binCSP, rowOrganized


def nary_ad_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only n-ary all-different
    constraints for both the row and column constraints.
    
    Returns a CSP object representing a Cageoky Grid CSP problem along with an array of variables
    for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using n-ary constraints to enforce row
    and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """
    boardSize = funpuzz_grid[0][0]
    basicDomain = []
    for i in range(boardSize):
        basicDomain.append(i + 1)

    boardVars = []
    rowOrganized = []
    colOrganized = []

    # set basic domain variables for all squares (left to right then up to down)
    for y in range(boardSize):
        newRow = []
        colOrganized.append([])
        for x in range(boardSize):
            varName = str(x + 1) + str(y + 1)
            var = Variable(varName, basicDomain)
            newRow.append(var)
        rowOrganized.append(newRow)

    for x in range(boardSize):
        for y in range(boardSize):
            colOrganized[y].append(rowOrganized[x][y])

    for y in range(boardSize):
        for x in range(boardSize):
            boardVars.append(rowOrganized[y][x])

    # boardVars is filled with 11, 21, 31, ... 12, 22, 32, etc

    # Now, we have to handle constraints
    # Almost exactly the same as binary constraints, except we will do them for whole columns and rows at a time
    possibleCombos = list(permutations(basicDomain, boardSize))

    naryCSP = CSP("naryNoCageCSP", boardVars)
    for rowNum in range(boardSize):
        consName = "RowBinConstraint" + str(rowNum+1)
        newRowCons = Constraint(consName, rowOrganized[rowNum])
        newRowCons.add_satisfying_tuples(possibleCombos)
        naryCSP.add_constraint(newRowCons)

    for colNum in range(boardSize):
        consName = "ColBinConstraint" + str(colNum+1)
        newColCons = Constraint(consName, colOrganized[colNum])
        newColCons.add_satisfying_tuples(possibleCombos)
        naryCSP.add_constraint(newColCons)

    return naryCSP, rowOrganized




def funpuzz_csp_model(funpuzz_grid):
    """A model built using your choice of (1) binary binary not-equal, or (2) n-ary all-different
    constraints for the grid, together with (3) funpuzz cage constraints. That is, you will
    choose one of the previous two grid models and expand it to include cage constraints
    for the funpuzz Variation.

    Returns a CSP object representing a Cageoky Grid CSP problem along with an array of variables
    for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using constraints
    to enforce cage, row and column constraints and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does require implementation of cage constraints.
    """

    boardSize = funpuzz_grid[0][0]
    basicDomain = []
    for i in range(boardSize):
        basicDomain.append(i + 1)

    totalCons = []
    boardVars = []
    rowOrganized = []
    colOrganized = []


    # set basic domain variables for all squares (left to right then up to down)
    for y in range(boardSize):
        newRow = []
        colOrganized.append([])
        for x in range(boardSize):
            varName = str(x + 1) + str(y + 1)
            var = Variable(varName, basicDomain)
            newRow.append(var)
        rowOrganized.append(newRow)


    for x in range(boardSize):
        for y in range(boardSize):
            colOrganized[y].append(rowOrganized[x][y])

    for y in range(boardSize):
        for x in range(boardSize):
            boardVars.append(rowOrganized[y][x])

    possibleCombos = list(permutations(basicDomain, 2))
    funCSP = CSP("funCSP", boardVars)

    # Now, we have all the basic row column constraints complete, so lets add Cage constraints to our CSP
    for cage in funpuzz_grid:
        if len(cage) == 1:
            continue
        # this is just telling us the size of the board, it is not a cage
        if len(cage) == 2:
            # make a constraint such that the only value for this cell can be the one given
            cell = str(cage[0])
            valueForCell = cage[1]
            cellX = cell[0]
            cellY = cell[1]
            varName = str(cellX) + str(cellY)
            rowOrganized[int(cellY) - 1][int(cellX) - 1] = Variable(varName, [valueForCell])

        elif len(cage) >= 2:
            involvedVars = []
            for celInd in range(len(cage) - 2):
                cell = str(cage[celInd])
                cellX = cell[0]
                cellY = cell[1]
                cellVar = rowOrganized[int(cellY) - 1][int(cellX) - 1]
                involvedVars.append(cellVar)

            cageGoal = cage[-2]
            possibleTups = []
            cageType = cage[-1]
            possibleCageCombos = list(product(basicDomain, repeat=len(involvedVars)))

            if cageType == 0:
                consName = "AdditionCons_" + str(cageGoal) + "_" + str(len(involvedVars))
                # addition
                for combo in possibleCageCombos:
                    if sum(combo) == cageGoal:
                        possibleTups.append(combo)

            elif cageType == 1:
                consName = "SubtractionCons_" + str(cageGoal) + "_" + str(len(involvedVars))
                # subtraction
                for combo in possibleCageCombos:
                    sub = combo[0]
                    for i in range(1, len(combo)):
                        sub = sub - combo[i]
                    if sub == cageGoal:
                        possibleTups.append(combo)

            elif cageType == 2:
                consName = "DivisionCons_" + str(cageGoal) + "_" + str(len(involvedVars))
                # division
                for combo in possibleCageCombos:
                    divy = combo[0]
                    for i in range(1, len(combo)):
                        divy = divy / combo[i]
                    if divy == cageGoal:
                        possibleTups.append(combo)

            elif cageType == 3:
                consName = "MultiplicationCons_" + str(cageGoal) + "_" + str(len(involvedVars))
                # multiplication
                for combo in possibleCageCombos:
                    prod = 1
                    for val in combo:
                        prod = prod * val
                    if prod == cageGoal:
                        possibleTups.append(combo)


            # print(cage)
            # print(involvedVars)
            # print(possibleTups)
            opConstraint = Constraint(consName, involvedVars)
            opConstraint.add_satisfying_tuples(possibleTups)
            totalCons.append(opConstraint)

        # For some reason, adding in the row/col constraints would not work and would give NONE

        # for row in rowOrganized:
        #     for v in row:
        #         for w in row:
        #             if not w is v:
        #                 consName = "RowBinConstraint" + v.name
        #                 newRowCons = Constraint(consName, [v, w])
        #                 newRowCons.add_satisfying_tuples(possibleCombos)
        #                 totalCons.append(newRowCons)
        #
        # for col in colOrganized:
        #     for v in col:
        #         for w in col:
        #             if not w is v:
        #                 consName = "ColBinConstraint" + v.name
        #                 newColCons = Constraint(consName, [v, w])
        #                 newColCons.add_satisfying_tuples(possibleCombos)
        #                 totalCons.append(newColCons)

    for const in totalCons:
        funCSP.add_constraint(const)

    return funCSP, rowOrganized


