# Look for #IMPLEMENT tags in this file.

"""
Construct and return funpuzz CSP models.
"""

from cspbase import *
import itertools


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
    dim = funpuzz_grid[0][0]
    domain = [i for i in range(1, dim + 1)]

    # Construct variable array
    variable_array = []
    for i in range(1, dim + 1):
        row = []
        for j in range(1, dim + 1):
            name = str(10 * i + j)
            var = Variable(name, domain)
            row.append(var)
        variable_array.append(row)
    
    # Possible value combination for binary not equal
    tuples = list(itertools.permutations(domain, 2))
   
    # Construct row and col constraints
    constraints = []
    for i in range(dim):
        for j in range(dim):
            var = variable_array[i][j]
            # Row constraints
            for col in range(j+1, dim):
                next_var = variable_array[i][col]
                cons_name = var.name + ',' + next_var.name
                cons_scope = [var, next_var]
                cons = Constraint(cons_name, cons_scope)
                cons.add_satisfying_tuples(tuples)
                constraints.append(cons)
            # Col constraints
            for row in range(i+1, dim):
                next_var = variable_array[row][j]
                cons_name = var.name + ',' + next_var.name
                cons_scope = [var, next_var]
                cons = Constraint(cons_name, cons_scope)
                cons.add_satisfying_tuples(tuples)
                constraints.append(cons)
    
    # Construct CSP 
    funpuzz_csp = CSP('binary_not_equal')
    for i in range(dim):
        for j in range(dim):
            funpuzz_csp.add_var(variable_array[i][j])
    
    for cons in constraints:
        funpuzz_csp.add_constraint(cons)
    
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
    dim = funpuzz_grid[0][0]
    domain = [i for i in range(1, dim + 1)]

    # Construct variable array
    variable_array = []
    for i in range(1, dim + 1):
        row = []
        for j in range(1, dim + 1):
            name = str(10 * i + j)
            var = Variable(name, domain)
            row.append(var)
        variable_array.append(row)
    
    # Possible value combination for n-ary all diff
    tuples = list(itertools.permutations(domain))   

    # Construct row and col constraints
    variable_array_T = list(zip(*variable_array))
    constraints = []
    for i in range(dim):
        cons_scope = variable_array[i]
        cons_name = 'row' + str(i+1)
        cons = Constraint(cons_name, cons_scope)
        cons.add_satisfying_tuples(tuples)
        constraints.append(cons)
        cons_scope = variable_array_T[i]
        cons_name = 'col' + str(i+1)
        cons = Constraint(cons_name, cons_scope)
        cons.add_satisfying_tuples(tuples)
        constraints.append(cons)
    
    # Construct CSP 
    funpuzz_csp = CSP('n-ary_all_diff')
    for i in range(dim):
        for j in range(dim):
            funpuzz_csp.add_var(variable_array[i][j])
    
    for cons in constraints:
        funpuzz_csp.add_constraint(cons)
    
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
    # I choose n-ary since it utilizes less storage
    funpuzz_csp, variable_array = nary_ad_grid(funpuzz_grid)
    
    dim = funpuzz_grid[0][0]
    domain = [i for i in range(1, dim+1)]
    
    # Add cage constraint
    constraints = []
    count = 0
    for cage in funpuzz_grid[1:]:
        # Update cage count
        count+=1

        # Obtain operator and target value
        op = cage[-1]
        target = cage[-2]
        
        # Set constraint name and obtain scope
        cons_name = 'cage' + str(count)
        cons_scope = []
        for cell in cage[:-2]:
            row, col = int(cell) // 10 - 1, int(cell) % 10 - 1
            cons_scope.append(variable_array[row][col])

        # Obtain constraint satisfying tuples
        num_operand = len(cage[:-2])
        possible_combination = itertools.combinations_with_replacement(domain, num_operand)
        tuples = []
        if op == 0: # +
            for comb in possible_combination:
                if sum(comb) == target:
                    tuples += list(itertools.permutations(comb))
        elif op == 1: #-
            for comb in possible_combination:
                permutation = list(itertools.permutations(comb))
                for perm in permutation:
                    diff = perm[0]
                    for val in perm[1:]:
                        diff -= val
                    if diff == target:
                        tuples += permutation
                        break
        elif op == 2: #/
            for comb in possible_combination:
                permutation = list(itertools.permutations(comb))
                for perm in permutation:
                    quotient = perm[0]
                    for val in perm[1:]:
                        quotient /= val
                    if quotient == target:
                        tuples += permutation
                        break
        elif op == 3: #*
            for comb in possible_combination:
                prod = 1
                for val in comb:
                    prod *= val
                if prod == target:
                    tuples += list(itertools.permutations(comb))

        # Build constraint
        cons = Constraint(cons_name, cons_scope)
        cons.add_satisfying_tuples(tuples)
        constraints.append(cons)

    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array
        