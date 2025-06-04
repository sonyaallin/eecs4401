#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

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
    funpuzz_csp = CSP("Funpuzz")
    variable_array = []

    # Create all variable objects
    for i in range(dim):
        variable_array.append([])
        for j in range(dim):
            variable_array[i].append(Variable("V" + str(i+1) + str(j+1), [v for v in range(1, dim+1)]))
            funpuzz_csp.add_var(variable_array[i][j])

    # Create satisfying tuple lists of pairs which are not the same
    tuples = [(v1+1, v2+1) for v1 in range(dim) for v2 in range(dim) if v1 != v2]

    # Create all constraints
    for i in range(dim):
        for j in range(dim):
            # Add constraints for all variables ahead (not behind as that is double counting)
            k = j + 1
            while k < dim:  # Variables to the right
                scope = [variable_array[i][j], variable_array[i][k]]
                name = "V" + str(i+1) + str(j+1) + " != " + "V" + str(i+1) + str(k+1)
                csp = Constraint(name, scope)
                csp.add_satisfying_tuples(tuples)
                funpuzz_csp.add_constraint(csp)
                k += 1

            k = i + 1
            while k < dim:  # Variables below
                scope = [variable_array[i][j], variable_array[k][j]]
                name = "V" + str(i+1) + str(j+1) + " != " + "V" + str(k+1) + str(j+1)
                csp = Constraint(name, scope)
                csp.add_satisfying_tuples(tuples)
                funpuzz_csp.add_constraint(csp)
                k += 1
    
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
    funpuzz_csp = CSP("Funpuzz")
    variable_array = []

    # Create all variable objects
    for i in range(dim):
        variable_array.append([])
        for j in range(dim):
            variable_array[i].append(Variable("V" + str(i+1) + str(j+1), [v for v in range(1, dim+1)]))
            funpuzz_csp.add_var(variable_array[i][j])

    # Create n-nary unique satisfying tuple lists
    tuples = list(itertools.permutations([v+1 for v in range(dim)]))

    # Create all constraints
    for i in range(dim):
        for j in range(dim):
            # Add row constraint
            scope = [variable_array[i][k] for k in range(dim)]
            name = "All_diff Row " + str(i+1)
            csp = Constraint(name, scope)
            csp.add_satisfying_tuples(tuples)
            funpuzz_csp.add_constraint(csp)

            # Add column constraint
            scope = [variable_array[k][j] for k in range(dim)]
            name = "All_diff Column " + str(j+1)
            csp = Constraint(name, scope)
            csp.add_satisfying_tuples(tuples)
            funpuzz_csp.add_constraint(csp)
    
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
    # return binary_ne_grid(funpuzz_grid)
    # return nary_ad_grid(funpuzz_grid)
    funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)

    i = 1   # Exclude 1st value of input
    while i < len(funpuzz_grid):
        j = 0
        op = funpuzz_grid[i][-1]
        target = funpuzz_grid[i][-2]
        funpuzz_grid[i]
        vars = []
        while j < len(funpuzz_grid[i]) - 2:
            vars.append(variable_array[funpuzz_grid[i][j]//10 - 1][funpuzz_grid[i][j]%10 - 1])
            j += 1

        scope = [vars[k] for k in range(len(vars))]
        name = "Cage, type: " + str(op)
        csp = Constraint(name, scope)

        tuples = get_constraint_tuples(vars, op, target)
        # print(scope)
        # print(tuples)
        # print()
        csp.add_satisfying_tuples(tuples)
        funpuzz_csp.add_constraint(csp)
        i += 1
        
    return funpuzz_csp, variable_array

def get_constraint_tuples(vars, op, target):
    '''Calls recursive functions that find all permutations of satisfying tuples'''

    # Handle differently depending on operation
    if op == 0:
        return add_constraint(vars, target, 0, 0, [])
    elif op == 1:
        tuples = sub_constraint(vars, target, 0, None, [])  # Only gets permutations with the first number subtracting
        total_tuples = []
        for t in tuples:
            extras = list(itertools.permutations(list(t)))
            for e in extras:
                if e not in total_tuples:
                    total_tuples.append(e)
        return total_tuples
    elif op == 2:
        tuples = div_constraint(vars, target, 0, None, [])  # Only gets permutations with the first number being the dividend
        total_tuples = []
        for t in tuples:    # Get's all non-duplicate permutations
            extras = list(itertools.permutations(list(t)))
            for e in extras:
                if e not in total_tuples:
                    total_tuples.append(e)
        return total_tuples
    elif op == 3:
        return mul_constraint(vars, target, 0, 1, [])
    
    return []

def add_constraint(vars, target, index, total, curr_tup):
    sat_tuples = []

    # Base case
    if index == len(vars) - 1:
        for i in range(vars[index].domain_size()):
            if total + (i+1) > target:
                return []
            elif total + (i+1) == target:
                return [tuple(curr_tup  + [i+1])]
    # Recursive case
    else:
        for i in range(vars[index].domain_size()):
            # Stops early as it is impossible to find satisfying tuple at this point
            if total + (i+1) >= target:
                return sat_tuples
            else:
                sat_tuples = sat_tuples + add_constraint(vars, target, index+1, total+(i+1), curr_tup + [i+1])

    return sat_tuples

def sub_constraint(vars, target, index, total, curr_tup):
    sat_tuples = []

    # Base case
    if index == len(vars) - 1:
        if total is None:   # Check for single elements
            return [(i,) for i in range(vars[index].domain_size()) if i == target]
        for i in range(vars[index].domain_size()):
            if total - (i+1) < target:
                return []
            elif total - (i+1) == target:
                return [tuple(curr_tup + [i+1])]
    # Recursive cases
    elif total is None:
        for i in range(vars[index].domain_size()):
            if (i+1) > target:   # This is the first value so the total is set
                sat_tuples = sat_tuples + sub_constraint(vars, target, index+1, (i+1), curr_tup + [i+1])
    else:
        for i in range(vars[index].domain_size()):
            # Stops early as it is impossible to find satisfying tuple at this point
            if total - (i+1) <= target:
                return sat_tuples
            else:
                sat_tuples = sat_tuples + sub_constraint(vars, target, index+1, total-(i+1), curr_tup + [i+1])

    return sat_tuples

def div_constraint(vars, target, index, total, curr_tup):
    sat_tuples = []

    # Base case
    if index == len(vars) - 1:
        if total is None:   # Check for single elements
            return [(i,) for i in range(vars[index].domain_size()) if i == target]
        for i in range(vars[index].domain_size()):
            if total / (i+1) < target:
                return []
            elif total / (i+1) == target:
                return [tuple(curr_tup + [i+1])]
    # Recursive cases
    elif total is None:
        for i in range(vars[index].domain_size()):
            if (i+1) >= target: # This is the first value so the total is set
                sat_tuples = sat_tuples + div_constraint(vars, target, index+1, (i+1), curr_tup + [i+1])
    else:
        for i in range(vars[index].domain_size()):
            # Stops early as it is impossible to find satisfying tuple at this point
            # If the number isn't whole, then it is also impossible to be satisfiable (target must be an integer)
            if total / (i+1) < target or total % (i+1) != 0:
                return sat_tuples
            else:
                sat_tuples = sat_tuples + div_constraint(vars, target, index+1, total-(i+1), curr_tup + [i+1])

    return sat_tuples

def mul_constraint(vars, target, index, total, curr_tup):
    sat_tuples = []

    # Base case
    if index == len(vars) - 1:
        for i in range(vars[index].domain_size()):
            if total * (i+1) > target:
                return []
            elif total * (i+1) == target:
                return [tuple(curr_tup  + [i+1])]
    # Recursive case
    else:
        for i in range(vars[index].domain_size()):
            # Stops early as it is impossible to find satisfying tuple at this point
            if total * (i+1) > target:
                return sat_tuples
            else:
                sat_tuples = sat_tuples + mul_constraint(vars, target, index+1, total*(i+1), curr_tup + [i+1])

    return sat_tuples