'''Classes for variable elimination Routines 
   A) class BN_Variable

	  This class allows one to define Bayes Net variables.

	  On initialization the variable object can be given a name and a
	  domain of values. This list of domain values can be added to or
	  deleted from in support of an incremental specification of the
	  variable domain.

	  The variable also has a set and get value method. These set a
	  value for the variable that can be used by the factor class. 


	B) class factor

	  This class allows one to define a factor specified by a table
	  of values. 

	  On initialization the variables the factor is over is
	  specified. This must be a list of variables. This list of
	  variables cannot be changed once the constraint object is
	  created.

	  Once created the factor can be incrementally initialized with a
	  list of values. To interact with the factor object one first
	  sets the value of each variable in its scope (using the
	  variable's set_value method), then one can set or get the value
	  of the factor (a number) on those fixed values of the variables
	  in its scope.

	  Initially, one creates a factor object for every conditional
	  probability table in the bayes-net. Then one initializes the
	  factor by iteratively setting the values of all of the factor's
	  variables and then adding the factor's numeric value using the
	  add_value method. 

	C) class BN
	   This class allows one to put factors and variables together to form a Bayes net.
	   It serves as a convient place to store all of the factors and variables associated
	   with a Bayes Net in one place. It also has some utility routines to, e.g,., find
	   all of the factors a variable is involved in. 

	'''

class Variable:
	'''Class for defining Bayes Net variables. '''
	
	def __init__(self, name, domain=[]):
		'''Create a variable object, specifying its name (a
		string). Optionally specify the initial domain.
		'''
		self.name = name                #text name for variable
		self.dom = list(domain)         #Make a copy of passed domain
		self.evidence_index = 0         #evidence value (stored as index into self.dom)
		self.assignment_index = 0       #For use by factors. We can assign variables values
										#and these assigned values can be used by factors
										#to index into their tables.

	def add_domain_values(self, values):
		'''Add domain values to the domain. values should be a list.'''
		for val in values: self.dom.append(val)

	def value_index(self, value):
		'''Domain values need not be numbers, so return the index
		   in the domain list of a variable value'''
		return self.dom.index(value)

	def domain_size(self):
		'''Return the size of the domain'''
		return(len(self.dom))

	def domain(self):
		'''return the variable domain'''
		return(list(self.dom))

	def set_evidence(self,val):
		'''set this variable's value when it operates as evidence'''
		self.evidence_index = self.value_index(val)

	def get_evidence(self):
		return(self.dom[self.evidence_index])

	def set_assignment(self, val):
		'''Set this variable's assignment value for factor lookups'''
		self.assignment_index = self.value_index(val)

	def get_assignment(self):
		return(self.dom[self.assignment_index])

	##These routines are special low-level routines used directly by the
	##factor objects
	def set_assignment_index(self, index):
		'''This routine is used by the factor objects'''
		self.assignment_index = index

	def get_assignment_index(self):
		'''This routine is used by the factor objects'''
		return(self.assignment_index)

	def __repr__(self):
		'''string to return when evaluating the object'''
		return("{}".format(self.name))
	
	def __str__(self):
		'''more elaborate string for printing'''
		return("{}, Dom = {}".format(self.name, self.dom))


class Factor: 

	'''Class for defining factors. A factor is a function that is over
	an ORDERED sequence of variables called its scope. It maps every
	assignment of values to these variables to a number. In a Bayes
	Net every CPT is represented as a factor. Pr(A|B,C) for example
	will be represented by a factor over the variables (A,B,C). If we
	assign A = a, B = b, and C = c, then the factor will map this
	assignment, A=a, B=b, C=c, to a number that is equal to Pr(A=a|
	B=b, C=c). During variable elimination new factors will be
	generated. However, the factors computed during variable
	elimination do not necessarily correspond to conditional
	probabilities. Nevertheless, they still map assignments of values
	to the variables in their scope to numbers.

	Note that if the factor's scope is empty it is a constaint factor
	that stores only one value. add_values would be passed something
	like [[0.25]] to set the factor's single value. The get_value
	functions will still work.  E.g., get_value([]) will return the
	factor's single value. Constaint factors migth be created when a
	factor is restricted.'''

	def __init__(self, name, scope):
		'''create a Factor object, specify the Factor name (a string)
		and its scope (an ORDERED list of variable objects).'''
		self.scope = list(scope)
		self.name = name
		size = 1
		for v in scope:
			size = size * v.domain_size()
		self.values = [0]*size  #initialize values to be long list of zeros.

	def get_scope(self):
		'''returns copy of scope...you can modify this copy without affecting 
		   the factor object'''
		return list(self.scope)

	def add_values(self, values):
		'''This routine can be used to initialize the factor. We pass
		it a list of lists. Each sublist is a ORDERED sequence of
		values, one for each variable in self.scope followed by a
		number that is the factor's value when its variables are
		assigned these values. For example, if self.scope = [A, B, C],
		and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
		C.domain() = ['heavy', 'light'], then we could pass add_values the
		following list of lists
		[[1, 'a', 'heavy', 0.25], [1, 'a', 'light', 1.90],
		 [1, 'b', 'heavy', 0.50], [1, 'b', 'light', 0.80],
		 [2, 'a', 'heavy', 0.75], [2, 'a', 'light', 0.45],
		 [2, 'b', 'heavy', 0.99], [2, 'b', 'light', 2.25],
		 [3, 'a', 'heavy', 0.90], [3, 'a', 'light', 0.111],
		 [3, 'b', 'heavy', 0.01], [3, 'b', 'light', 0.1]]

		 This list initializes the factor so that, e.g., its value on
		 (A=2,B=b,C='light) is 2.25'''

		for t in values:
			index = 0
			for v in self.scope:
				index = index * v.domain_size() + v.value_index(t[0])
				t = t[1:]
			self.values[index] = t[0]
		 
	def add_value_at_current_assignment(self, number): 

		'''This function allows adding values to the factor in a way
		that will often be more convenient. We pass it only a single
		number. It then looks at the assigned values of the variables
		in its scope and initializes the factor to have value equal to
		number on the current assignment of its variables. Hence, to
		use this function one first must set the current values of the
		variables in its scope.

		For example, if self.scope = [A, B, C],
		and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
		C.domain() = ['heavy', 'light'], and we first set an assignment for A, B
		and C:
		A.set_assignment(1)
		B.set_assignment('a')
		C.set_assignment('heavy')
		then we call 
		add_value_at_current_assignment(0.33)
		 with the value 0.33, we would have initialized this factor to have
		the value 0.33 on the assigments (A=1, B='1', C='heavy')
		This has the same effect as the call
		add_values([1, 'a', 'heavy', 0.33])

		One advantage of the current_assignment interface to factor values is that
		we don't have to worry about the order of the variables in the factor's
		scope. add_values on the other hand has to be given tuples of values where 
		the values must be given in the same order as the variables in the factor's 
		scope. 

		See recursive_print_values called by print_table to see an example of 
		where the current_assignment interface to the factor values comes in handy.
		'''

		index = 0
		for v in self.scope:
			index = index * v.domain_size() + v.get_assignment_index()
		self.values[index] = number

	def get_value(self, variable_values):

		'''This function is used to retrieve a value from the
		factor. We pass it an ordered list of values, one for every
		variable in self.scope. It then returns the factor's value on
		that set of assignments.  For example, if self.scope = [A, B,
		C], and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
		C.domain() = ['heavy', 'light'], and we invoke this function
		on the list [1, 'b', 'heavy'] we would get a return value
		equal to the value of this factor on the assignment (A=1,
		B='b', C='light')'''

		index = 0
		for v in self.scope:
			index = index * v.domain_size() + v.value_index(variable_values[0])
			variable_values = variable_values[1:]
		return self.values[index]

	def get_value_at_current_assignments(self):

		'''This function is used to retrieve a value from the
		factor. The value retrieved is the value of the factor when
		evaluated at the current assignment to the variables in its
		scope.

		For example, if self.scope = [A, B, C], and A.domain() =
		[1,2,3], B.domain() = ['a', 'b'], and C.domain() = ['heavy',
		'light'], and we had previously invoked A.set_assignment(1),
		B.set_assignment('a') and C.set_assignment('heavy'), then this
		function would return the value of the factor on the
		assigments (A=1, B='1', C='heavy')'''
		
		index = 0
		for v in self.scope:
			index = index * v.domain_size() + v.get_assignment_index()
		return self.values[index]

	def print_table(self):
		'''print the factor's table'''
		saved_values = []  #save and then restore the variable assigned values.
		for v in self.scope:
			saved_values.append(v.get_assignment_index())

		self.recursive_print_values(self.scope)

		for v in self.scope:
			v.set_assignment_index(saved_values[0])
			saved_values = saved_values[1:]
		
	def recursive_print_values(self, vars):
		if len(vars) == 0:
			print("[",end=""),
			for v in self.scope:
				print("{} = {},".format(v.name, v.get_assignment()), end="")
			print("] = {}".format(self.get_value_at_current_assignments()))
		else:
			for val in vars[0].domain():
				vars[0].set_assignment(val)
				self.recursive_print_values(vars[1:])

	def __repr__(self):
		return("{}".format(self.name))

class BN:

	'''Class for defining a Bayes Net.
	   This class is simple, it just is a wrapper for a list of factors. And it also
	   keeps track of all variables in the scopes of these factors'''

	def __init__(self, name, Vars, Factors):
		self.name = name
		self.Variables = list(Vars)
		self.Factors = list(Factors)
		for f in self.Factors:
			for v in f.get_scope():     
				if not v in self.Variables:
					print("Bayes net initialization error")
					print("Factor scope {} has variable {} that", end='')
					print(" does not appear in list of variables {}.".format(list(map(lambda x: x.name, f.get_scope())), v.name, list(map(lambda x: x.name, Vars))))

	def factors(self):
		return list(self.Factors)

	def variables(self):
		return list(self.Variables)

'''
############## Notes/Questions/Clarity on Implementation ##############
- Evidence variables not included in name due to inability to detect if variable is an evidence var
  outside of VE() function, if multiple evidence vars in factor, etc. Tracking evidence variables
  for the Query variable should be done prior to Variable Elimination call/does not need to be specified
  in factor's name.
- Naming for when factor has no variables in scope (e.g. summing out only var in scope):
	Will be left as "P()"
- Naming for when factor is a Constant factor (no variables in scope but has one value in CPT):
	If Constant factor, name is "P(var = val)". If not, name is "P(scope without restricted var)"

multiply_factors():
	1. Create all combinations of assignments for extended/new list of variables
	2. Go through each combination in new CPT to achieve relevant combination for each old CPT/factor
	3. Get values in each old CPT/factor and multiply together for product

restrict_factor():
	1. Create all combintations of assignments for old CPT/factor
	2. For all combinations/rows that contain the evidence value for the evidence variable, take those
	   rows for the new CPT
	In general, new scope is old scope minus the evidence variable. But if old scope only has one variable
	(is a Constant factor), new scope is old scope (evidence variable not taken out) for stability reasons
	(functions require a scope to iterate over).

sum_out_variable():
	1. Create all combinations of assignments for old factor's scope/list of variables
	2. Go through each combination/row and set assignment for all variables that are not the var to sum out.
	   This means that all variables in new factor's scope is assigned.
	3. Get assignment value for both old and new CPT, and add old assignment to new assignment.
	   Each row in old CPT will be accessed once, but each row in new CPT will be accessed var.domain_size()
	   times.
	Here, new scope is old scope minus the variable to sum out. To note that if old factor only has one
	variable in its scope, it is still removed (as per test case results). Factor will have scope=[], and
	name= "P()".

VE():
	1. Restrict factors for all evidence variables in its scope
	2. For remaining variables: multiply corresponding factors, then sum out variable
	3. When only the Query variable remaining, multiply factors (if more than one factor), then normalize 
	to get list of probabilities

	In Step 3, remaining factors in factor list should only have Query Var or Evidence Vars left in its scope.
	Only factors with the Query variable need be taken into consideration at this point. Evidence variables 
	can be included here (multiplied/summed out/normalized) but will ultimately lead to same result as if 
	just factors with Query var were taken. Is also cleaner for edge cases (e.g. if Constant factor or factor 
	with all variables summed out are remaining).
'''

# variable to print out values at checkpoints (if True); no impact to result if set to True/False
debugging = False
import itertools

def multiply_factors(Factors):
	'''return a new factor that is the product of the factors in Factors'''
	
	if debugging:
		print("Starting multiply_factors")
		for f in range(len(Factors)):
			print("old CPT for {} (# {}): ".format(Factors[f].name, f+1))
			Factors[f].print_table()
	# get list of variables for new factor
	var_list = []
	for factor in Factors:
		for var in factor.get_scope():
			if var not in var_list:
				var_list.append(var)
	# init new factor
	name = listToString(var_list)
	new_factor = Factor("P({})".format(name), var_list)

	# find all combinations for assignments
	domain_list = []
	for var in var_list:
		domain_list.append(var.domain())
	new_CPT = itertools.product(*domain_list)
	new_CPT = [list(row) for row in new_CPT]
	
	# need to find product for each row/assignment in new CPT
	for row in new_CPT:
		# loop thru factors to get values for product
		productHolder = 1
		for factor in Factors:
			# need combination for vars for old CPT
			old_CPT_combination = []
			# go thru vars in old CPT
			for var in factor.get_scope():
				# get index of this var in new CPT
				for i in range(len(var_list)):
					# use index to get var's assignment
					if var == var_list[i]:
						# append to this factors assignment/combination
						# end up with ordered combination for lookup in old CPT
						old_CPT_combination.append(row[i])
			# index to get value in old CPT
			productHolder *= factor.get_value(old_CPT_combination)
		row.append(productHolder)

	new_factor.add_values(new_CPT)
	if debugging:
		print("new_CPT for {}:".format(new_factor.name))
		new_factor.print_table()
		print("Ending multiply_factors")
	return new_factor

def restrict_factor(f, var, value):
	'''f is a factor, var is a Variable, and value is a value from var.domain.
	Return a new factor that is the restriction of f by this var = value.
	Don't change f! If f has only one variable its restriction yields a
	constant factor'''

	if debugging:
		print("Starting restrict_factor for var: {}, value: {}".format(var, value))
		print("old CPT for {}:".format(f.name))
		f.print_table()
	
	# init new factor with scope without evidence var
	scope = f.get_scope()
	# if is a constant factor
	isConstantFactor = False
	if len(scope) == 1:
		isConstantFactor = True
	# give more specific name if a constant factor
	if isConstantFactor:
		name = "P({}={})".format(var.name, value)
	else:
		# var is removed from scope unless a constant var
		scope.remove(var)
		name = "P({})".format(listToString(scope))
	new_factor = Factor(name, scope)

	# find all combinations for assignments in var (old_CPT)/before restriction of var
	domain_list = []
	for v in f.get_scope():
		domain_list.append(v.domain())
	old_CPT = itertools.product(*domain_list)
	old_CPT = [list(row) for row in old_CPT]
	# index of var in scope of f
	var_index = f.get_scope().index(var)

	# go thru each row in old CPT, take rows that have value/evidence
	new_CPT = []
	for i in range(len(old_CPT)):
		if value == old_CPT[i][var_index]:
			new_CPT.append(old_CPT[i])
			# don't remove assignment from CPT row if it's the only assignment
			if not isConstantFactor:
				del new_CPT[-1][var_index]
			new_CPT[-1].append(f.values[i])

	# add new CPT to new Factor
	new_factor.add_values(new_CPT)
	if debugging:
		print("new_CPT for {}:".format(new_factor.name))
		new_factor.print_table()
		print("Ending restrict_factor")
	return new_factor


def sum_out_variable(f, var):
	'''return a new factor that is the product of the factors in Factors
	   followed by the suming out of Var'''
	
	if debugging:
		print("Starting sum_out_var")
		print("old CPT for {}:".format(f.name))
		f.print_table()

	# initializing new Factor object
	scope = f.get_scope()
	scope.remove(var)
	name = listToString(scope)
	new_factor = Factor("P({})".format(name), scope)

	# find all combinations for assignments in old_CPT before summing of var
	domain_list = []
	for v in f.get_scope():
		domain_list.append(v.domain())
	old_CPT = itertools.product(*domain_list)
	old_CPT = [list(row) for row in old_CPT]

	# list of scope (variables)
	oldFactorScope = f.get_scope()

	for row in old_CPT:
		# get value in old CPT
		OldCPT_val = f.get_value(row)

		# assign all vars minus var to sum out
		for i in range(len(oldFactorScope)):
			if oldFactorScope[i] != var:
				oldFactorScope[i].set_assignment(row[i])
		# all vars in new factor should be assigned
		curr_val = new_factor.get_value_at_current_assignments()
		# add old val to new CPT
		currToUpdate = curr_val + OldCPT_val
		new_factor.add_value_at_current_assignment(currToUpdate)

	# Restoring assignments/unassigning vars:
	#	 Setting assignment_index to 0 for all vars in factor
	for v in oldFactorScope:
		v.set_assignment_index(0)
	
	if debugging:	
		print("new_CPT for {}:".format(new_factor.name))
		new_factor.print_table()
		print("Ending sum_out_var")
	return new_factor


def nextFalseIndex(visitedList):
	''' To return first index that is False in a list of booleans; if no Falses, return False '''
	ind = 0
	for boolean in visitedList:
		if boolean == False:
			return ind
		ind += 1
	return False

def listToString(listToConvert):
	string = ""
	for word in listToConvert:
		string += word.name + ", "

	return string[:-2]

def normalize(nums):
	'''take as input a list of number and return a new list of numbers where
	now the numbers sum to 1, i.e., normalize the input numbers'''
	s = sum(nums)
	if s == 0:
		newnums = [0]*len(nums)
	else:
		newnums = []
		for n in nums:
			newnums.append(n/s)
	return newnums

###Orderings
def min_fill_ordering(Factors, QueryVar):
	'''Compute a min fill ordering given a list of factors. Return a list
	of variables from the scopes of the factors in Factors. The QueryVar is 
	NOT part of the returned ordering'''
	scopes = []
	for f in Factors:
		scopes.append(list(f.get_scope()))
	Vars = []
	for s in scopes:
		for v in s:
			if not v in Vars and v != QueryVar:
				Vars.append(v)
	
	ordering = []
	while Vars:
		(var,new_scope) = min_fill_var(scopes,Vars)
		ordering.append(var)
		if var in Vars:
			Vars.remove(var)
		scopes = remove_var(var, new_scope, scopes)
	return ordering

def min_fill_var(scopes, Vars):
	'''Given a set of scopes (lists of lists of variables) compute and
	return the variable with minimum fill in. That the variable that
	generates a factor of smallest scope when eliminated from the set
	of scopes. Also return the new scope generated from eliminating
	that variable.'''
	minv = Vars[0]
	(minfill,min_new_scope) = compute_fill(scopes,Vars[0])
	for v in Vars[1:]:
		(fill, new_scope) = compute_fill(scopes, v)
		if fill < minfill:
			minv = v
			minfill = fill
			min_new_scope = new_scope
	return (minv, min_new_scope)

def compute_fill(scopes, var):
	'''Return the fill in scope generated by eliminating var from
	scopes along with the size of this new scope'''
	union = []
	for s in scopes:
		if var in s:
			for v in s:
				if not v in union:
					union.append(v)
	if var in union: union.remove(var)
	return (len(union), union)

def remove_var(var, new_scope, scopes):
	'''Return the new set of scopes that arise from eliminating var
	from scopes'''
	new_scopes = []
	for s in scopes:
		if not var in s:
			new_scopes.append(s)
	new_scopes.append(new_scope)
	return new_scopes
			
		
###
def VE(Net, QueryVar, EvidenceVars):
	'''
	Input: Net---a BN object (a Bayes Net)
		   QueryVar---a Variable object (the variable whose distribution
					  we want to compute)
		   EvidenceVars---a LIST of Variable objects. Each of these
						  variables has had its evidence set to a particular
						  value from its domain using set_evidence. 

	VE returns a distribution over the values of QueryVar, i.e., a list
	of numbers one for every value in QueryVar's domain. These numbers
	sum to one, and the i'th number is the probability that QueryVar is
	equal to its i'th value given the setting of the evidence
	variables. For example if QueryVar = A with Dom[A] = ['a', 'b',
	'c'], EvidenceVars = [B, C], and we have previously called
	B.set_evidence(1) and C.set_evidence('c'), then VE would return a
	list of three numbers. E.g. [0.5, 0.24, 0.26]. These numbers would
	mean that Pr(A='a'|B=1, C='c') = 0.5 Pr(A='a'|B=1, C='c') = 0.24
	Pr(A='a'|B=1, C='c') = 0.26
	'''
	if debugging:
		print("")
		print("Starting Variable Elimination")
		print("queryvar is: {}".format(QueryVar))

	# to restore original Net.Factors later
	originalFactors = {}
	origFactorSize = len(Net.Factors)
	for i in range(origFactorSize):
		originalFactors[i] = Net.Factors[i]

	# init list of factors to work with; to be updated thru-out process (thus need copy)
	factor_list = Net.Factors
	if debugging:
		print(factor_list)
	
	# first restrict all factors for all evidence variables it has in its scope
	for evidenceVar in EvidenceVars:
		tmpFactor_list_add = []
		tmpFactor_list_remove = []
		for factor in factor_list:
			# factor has evidence var in scope; thus, restrict factor
			if evidenceVar in factor.get_scope():
				new_factor = restrict_factor(factor, evidenceVar, evidenceVar.get_evidence())
				tmpFactor_list_remove.append(factor)
				tmpFactor_list_add.append(new_factor)
		for toRemove in tmpFactor_list_remove:
			factor_list.remove(toRemove)
		for toAdd in tmpFactor_list_add:
			factor_list.append(toAdd)

	# get remaining variables (variables not evidence vars or the query var)
	remainingVars = []
	for var in Net.Variables:
		# assuming QueryVar is a single var, not list of vars
		if var not in EvidenceVars and var != QueryVar:
			remainingVars.append(var)
	
	if debugging:
		print(factor_list)

	for remainingVar in remainingVars:
		factorsToMultiply = []
		# for all factors that have this remaining var, multiply them together/sum out for that var
		for factor in factor_list:
			if remainingVar in factor.get_scope():
				factorsToMultiply.append(factor)

		if debugging:
			print("Remaining variable: {} | Factors to mulitply: {}".format(remainingVar, factorsToMultiply))
		productFactor = multiply_factors(factorsToMultiply)

		summedFactor = sum_out_variable(productFactor, remainingVar)

		for factorToRemove in factorsToMultiply:
			factor_list.remove(factorToRemove)
		factor_list.append(summedFactor)
		
		if debugging:
			print(factor_list)
	
	if debugging:
		print(factor_list)

	# take remaining factors with Query Var in its scope
	factorsWithQueryVar = []
	for factor in factor_list:
		if QueryVar in factor.get_scope():
			factorsWithQueryVar.append(factor)

	# multiply remaining factors and normalize for final probability list
	# multiply_factors() handles whether one or several factors to multiply together
	productQueryFactor = multiply_factors(factorsWithQueryVar)
	res = productQueryFactor.values
	res = normalize(res)
	if debugging:
		print("Final result: {}".format(res))

	# restore original Factor list in Bayes Net object
	factor_list = []
	for i in range(origFactorSize):
		factor_list.append(originalFactors[i])
	Net.Factors = factor_list

	return res
