#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import product, permutations

### Helper Functions ###
def populate_variable_array(csp, n) -> list:
	""" Populate an nxn funpuzz grid with Variable objects
	Returns a 2D array of Variable objects with variable_array[i][j]
	representing the cell name {i+1}{j+1} (since cell names start from 11 to nn)
	Each variable has domain 1 to n, inclusive
	"""
	variable_array = []
	for i in range(0, n):
		row_vars = []
		for j in range(0, n):
			# Cell names encoded as integers from 11 to nn
			# Empty cells can be filled with integer from 1 to n
			new_var = Variable("{}{}".format(i+1, j+1), list(range(1, n+1)))
			row_vars.append(new_var)
			csp.add_var(new_var)

		variable_array.append(row_vars)

	return variable_array

def generate_all_var_domain_combs(variables):
	""" Takes a list of variables as input and generates all possible
	combinations of variables values given their domains. Returns a
	list of tuples which each tuple representing a unique cartesian
	product.
	"""
	var_domains = [var.cur_domain() for var in variables]
	all_combinations = list(product(*var_domains))
	return all_combinations

def reduce_values(values: tuple, operator: int) -> float:
	# addition
	result = 0
	if operator == 0:
		for val in values:
			result += val
	# subtraction
	elif operator == 1:
		result = values[0]
		for val in values[1:]:
			result -= val
	# division
	elif operator == 2:
		result = values[0]
		for val in values[1:]:
			result /= val
	# multiplication
	elif operator == 3:
		result = 1
		for val in values:
			result *= val
	else:
		raise ValueError("Specified operator is invalid.")

	return result

def generate_sat_binary_tuples(var1: Variable, var2: Variable):
	""" Generate all satisfactory binary tuples between the two input variables
	by taking cartesian product of each member of var1 and var2 and returning
	those which are satisfactory as a list of tuples.
	"""
	tuples = []

	# manual cartesian product
	for mem1 in var1.cur_domain():
		for mem2 in var2.cur_domain():
			# if members not equal, this tuple is satisfactory
			if mem1 != mem2:
				tuples.append((mem1, mem2))

	return tuples

def generate_sat_n_ary_tuples(variables: list):
	""" Generate all satisfactory n-ary tuples between the list of variables
	by taking cartesian product of variable domains and returning
	those which are satisfactory as a list of tuples.
	"""
	tuples = []

	# get list of all variable domains in order to perform cartesian prod
	all_combinations = generate_all_var_domain_combs(variables)
	# check each combination for duplicates; if duplicate member exists,
	# then combination is not a satisfactory constraint
	for comb in all_combinations:
		# this is only true when comb doesn't contain duplicates
		# otherwise, the length of the set will be less than length of vars
		if len(set(comb)) == len(variables):
			tuples.append(tuple(comb))

	return tuples

def generate_sat_cage_tuples(variables: list, operator: int, target: int):
	""" Generate all satisfactory cage tuples between the list of variables
	based on the operator and target provided and returning those which are
	satisfactory as a list of tuples.
	"""
	# addition
	all_combinations = generate_all_var_domain_combs(variables)

	sat_tuples = []

	for comb in all_combinations:
		# DUPLICATES ARE ALLOWED FOR CAGE CONSTRAINTS
		# ;_; spent so long debugging before realizing this

		# Also any permutation of the cells and their values which result
		# in target is viable. 
		for c_perm in permutations(comb):
			if reduce_values(c_perm, operator) == float(target):
				sat_tuples.append(comb)

	return sat_tuples

### End of Helper Functions ###

def binary_ne_grid(funpuzz_grid):
	"""A model of a funpuzz grid (without cage constraints) built using only
	binary all-different constraints for both the row and column constraints.

	Returns a CSP object representing a FunPuzz Grid CSP problem along with an
	array of variables for the problem. That is return:

	funpuzz_csp, variable_array

	where funpuzz_csp is a csp representing funpuzz grid using binary constraints
	to enforce row and column constraints and variable_array is a list of lists:

	   [ [  ]
		 [  ]
		 .
		 .
		 .
		 [  ] ]

	such that variable_array[i][j] is the Variable (object) that you built to
	represent the value to be placed in cell i,j of the funpuzz Grid.

	Note that this model does not require implementation of cage constraints.
	"""
	# get dimension of grid
	n = funpuzz_grid[0][0]
	funpuzz_csp = CSP("binary_ne_grid")
	variable_array = populate_variable_array(funpuzz_csp, n)

	# row constraints
	for i in range(n):
		for j in range(n):
			for k in range(j+1, n):
				var1 = variable_array[i][j]
				var2 = variable_array[i][k]
				cons = Constraint("C({}{},{}{})".format(i+1, j+1, i+1, k+1),
									[var1, var2])
				tuples = generate_sat_binary_tuples(var1, var2)
				cons.add_satisfying_tuples(tuples)
				funpuzz_csp.add_constraint(cons)

	# column constraints
	for j in range(n):
		for i in range(n):
			for k in range(i+1, n):
				var1 = variable_array[i][j]
				var2 = variable_array[k][j]
				cons = Constraint("C({}{},{}{})".format(i+1, j+1, k+1, j+1),
									[var1, var2])
				tuples = generate_sat_binary_tuples(var1, var2)
				cons.add_satisfying_tuples(tuples)
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
	n = funpuzz_grid[0][0]
	funpuzz_csp = CSP("nary_ad_grid")
	variable_array = populate_variable_array(funpuzz_csp, n)

	# row constraints
	for (row, row_vars) in enumerate(variable_array):

		# format constraint name to include all row variables
		cons_name = ""
		for col in range(0, n):
			cons_name += "{}{},".format(row+1, col+1)

		cons = Constraint("C({})".format(cons_name[:-1]), row_vars)
		tuples = generate_sat_n_ary_tuples(row_vars)
		cons.add_satisfying_tuples(tuples)
		funpuzz_csp.add_constraint(cons)

	# col constraints
	for col in range(0, n):
		col_vars = []
		cons_name = ""
		for row in range(0, n):
			col_vars.append(variable_array[row][col])
			cons_name += "{}{},".format(row+1, col+1)

		cons = Constraint("C({})".format(cons_name[:-1]), col_vars)
		tuples = generate_sat_n_ary_tuples(col_vars)
		cons.add_satisfying_tuples(tuples)
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
	funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)
	# funpuzz_csp, variable_array = nary_ad_grid(funpuzz_grid)
	cages = funpuzz_grid[1:]

	op_mappings = {0: '+', 1: '-', 2: '/', 3: '*'}

	for cage in cages:
		if len(cage) == 2:
			# if list has two elements, the first correspoonds to a cell
			# the second corresponds to the target
			i = int(cage[0]/10)-1
			j = int(cage[0]%10)-1
			cons = Constraint("C({})={}".format(cage[0], cage[1]), variable_array[i][j])
			cons.add_satisfying_tuples([cage[1]])
			funpuzz_csp.add_constraint(cons)

		else:
			# first n elements correspond to cells, element at index n corresponds to target
			# and last element corresponds to operator

			# number of cells is length of cage minus target and operator
			n = len(cage) - 2

			operator = cage[-1]
			target = cage[n]
			cells = cage[:n]

			cons_name = ""

			variables = []
			for cell in cells:
				i = int(cell/10)-1
				j = int(cell%10)-1
				variables.append(variable_array[i][j])
				cons_name += "{}{}".format(cell, op_mappings.get(operator))

			tuples = generate_sat_cage_tuples(variables, operator, target)
			cons = Constraint("C({})={}".format(cons_name[:-1], target), variables)
			cons.add_satisfying_tuples(tuples)
			funpuzz_csp.add_constraint(cons)

	return funpuzz_csp, variable_array

