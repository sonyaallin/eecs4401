#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import combinations, permutations, chain, combinations_with_replacement

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
    N = funpuzz_grid[0][0]
    DOMAIN = range(1, N + 1)
    ALLPERMUTATIONS = list(permutations(DOMAIN, r=2))              # Valid pairings for binary constraints 
    # variable_array = [Variable(f'V{x}{y}', DOMAIN) for x, y in product(DOMAIN, repeat=2)]
    variable_array = [[Variable(f'V{x}{y}', DOMAIN) for y in DOMAIN] for x in DOMAIN]   # Need it to be 2D
    funpuzz_csp = CSP(f'BINARY {N}x{N}', list(chain.from_iterable(variable_array)))
    for i in range(N):
        for x, y in combinations(variable_array[i], 2):
            constraint = Constraint(f'ROW PAIR {x.name} {y.name}', [x, y])  # Add possible permutations
            constraint.add_satisfying_tuples(ALLPERMUTATIONS)                  # to row constraints
            funpuzz_csp.add_constraint(constraint)
        for x, y in combinations([row[i] for row in variable_array], 2):
            constraint = Constraint(f'COL PAIR {x.name} {y.name}', [x, y])  # Add possible permutations
            constraint.add_satisfying_tuples(ALLPERMUTATIONS)                  # to col constraints
            funpuzz_csp.add_constraint(constraint)
    return funpuzz_csp, variable_array


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
    N = funpuzz_grid[0][0]
    DOMAIN = range(1, N + 1)
    ALLPERMUTATIONS = list(permutations(DOMAIN))                   # Valid pairings for n-ary constraints 
    # variable_array = [Variable(f'V{x}{y}', DOMAIN) for x, y in product(DOMAIN, repeat=2)]
    variable_array = [[Variable(f'V{x}{y}', DOMAIN) for y in DOMAIN] for x in DOMAIN]   # Need it to be 2D
    funpuzz_csp = CSP(f'N-ARY {N}x{N}', list(chain.from_iterable(variable_array)))
    for i in range(N):
        constraint = Constraint(f'ROW {i+1}', variable_array[i])        # Add possible permutations
        constraint.add_satisfying_tuples(ALLPERMUTATIONS)                  # to row constraints
        funpuzz_csp.add_constraint(constraint)
        constraint = Constraint(f'COL {i+1}', [row[i] for row in variable_array])  # Add possible permutations
        constraint.add_satisfying_tuples(ALLPERMUTATIONS)                  # to col constraints
        funpuzz_csp.add_constraint(constraint)
    return funpuzz_csp, variable_array


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
    ######################################## FROM BINARY NE GRID ########################################
    N = funpuzz_grid[0][0]
    DOMAIN = range(1, N + 1)
    ALLPERMUTATIONS = list(permutations(DOMAIN, r=2))              # Valid pairings for binary constraints 
    # variable_array = [Variable(f'V{x}{y}', DOMAIN) for x, y in product(DOMAIN, repeat=2)]
    variable_array = [[Variable(f'V{x}{y}', DOMAIN) for y in DOMAIN] for x in DOMAIN]   # Need it to be 2D
    funpuzz_csp = CSP(f'FUNPUZZ {N}x{N}', list(chain.from_iterable(variable_array)))
    for i in range(N):
        for x, y in combinations(variable_array[i], 2):
            constraint = Constraint(f'ROW PAIR {x.name} {y.name}', [x, y])  # Add possible permutations
            constraint.add_satisfying_tuples(ALLPERMUTATIONS)                  # to row constraints
            funpuzz_csp.add_constraint(constraint)
        for x, y in combinations([row[i] for row in variable_array], 2):
            constraint = Constraint(f'COL PAIR {x.name} {y.name}', [x, y])  # Add possible permutations
            constraint.add_satisfying_tuples(ALLPERMUTATIONS)                  # to col constraints
            funpuzz_csp.add_constraint(constraint)
    ######################################## FROM BINARY NE GRID ########################################

    for cage_constraint in funpuzz_grid[1:]:
        LENGTH = len(cage_constraint)
        if LENGTH == 2:    # (CELL, TARGET) for 2 element constraints
            x, y = cage_constraint[0] // 10, cage_constraint[0] % 10
            constraint = Constraint(f'CELL {x}{y}', [variable_array[x - 1][y - 1]])
            constraint.add_satisfying_tuples([(cage_constraint[1],)])
            funpuzz_csp.add_constraint(constraint)
        elif LENGTH > 2:    # (CELL, ..., TARGET, OPERATION) for 3+ element constraints
            operator = cage_constraint[-1]
            target = cage_constraint[-2]
            valid, constraint_array, row, col = [], [], [], []    # Valid tuples, Cage Cells, Row values, Col values
            for i in cage_constraint[:-2]:
                x, y = i // 10 - 1, i % 10 - 1
                constraint_array.append(variable_array[x][y])
                row.append(x)
                col.append(y)
            NUM_CONSTRAINT = len(constraint_array)
            constraint = Constraint(f'CAGE C{i}', constraint_array)
            # Cut down combinations when we know the cage is a unit row or col rectangle (All dif constraints)
            ALLCOMBINATIONS = (list(combinations(DOMAIN, NUM_CONSTRAINT)) if row.count(row[0]) == NUM_CONSTRAINT or
            col.count(col[0]) == NUM_CONSTRAINT else list(combinations_with_replacement(DOMAIN, NUM_CONSTRAINT)))

            def sub(permutation):
                '''Return total subtraction from permutation ordering'''
                curr = permutation[0]
                for value in permutation[1:]:
                    curr -= value
                return curr

            def div(permutation):
                '''Return total division from permutation ordering'''
                curr = permutation[0]
                for value in permutation[1:]:
                    curr /= value
                return curr
            
            def prod(combination):
                '''Return total product from combination'''
                curr = combination[0]
                for value in combination[1:]:
                    curr *= value
                return curr

            for combination in ALLCOMBINATIONS:     # Add valid permutations from combinations for each operator
                notfound = True
                
                # Addition and multiplication do not need permutation
                if operator == 0:                   # ADDITION
                    if sum(combination) == target:
                        valid.extend(list(permutations(combination)))
                elif operator == 3:                 # MULTIPLICATION
                    if prod(combination) == target:
                        valid.extend(list(permutations(combination)))
                # Subtraction and Division need permutation
                elif operator == 1:                 # SUBTRACTION
                    perm_of_comb = list(permutations(combination))
                    while notfound and perm_of_comb:
                        if sub(perm_of_comb.pop()) == target:
                            valid.extend(list(permutations(combination)))
                            notfound = False
                elif operator == 2:                 # DIVISION
                    perm_of_comb = list(permutations(combination))
                    while notfound and perm_of_comb:
                        if div(perm_of_comb.pop()) == target:
                            valid.extend(list(permutations(combination)))
                            notfound = False
                            
            constraint.add_satisfying_tuples(valid)
            funpuzz_csp.add_constraint(constraint)

    return funpuzz_csp, variable_array
