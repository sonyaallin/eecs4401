#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes for variable elimination Routines
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
    This class allows one to put factors and variables together
    to form a Bayes net. It serves as a convenient place to store all of the
    factors and variables associated with a Bayes Net in one place. It also
    has some utility routines to, e.g,., find all of the factors a variable
    is involved in.
"""
from typing import List, Optional, Tuple
from itertools import product


class Variable:
    """Class for defining Bayes Net variables. """
    
    def __init__(self, name: str, domain: Optional[list] = None):
        """Create a variable object, specifying its name (a
        string). Optionally specify the initial domain.
        """
        # text name for variable
        self.name = name
        # Make a copy of passed domain
        self.dom = list(domain) if domain else []
        # evidence value (stored as index into self.dom)
        self.evidence_index = 0
        # For use by factors. We can assign variables values
        self.assignment_index = 0
        # and these assigned values can be used by factors
        # to index into their tables.
    
    def add_domain_values(self, values: list) -> None:
        """Add domain values to the domain. values should be a list."""
        for val in values:
            self.dom.append(val)
    
    def value_index(self, value) -> int:
        """Domain values need not be numbers, so return the index
           in the domain list of a variable value"""
        return self.dom.index(value)
    
    def domain_size(self) -> int:
        """Return the size of the domain"""
        return len(self.dom)
    
    def domain(self) -> list:
        """return the variable domain"""
        return list(self.dom)
    
    def set_evidence(self, val) -> None:
        """set this variable's value when it operates as evidence"""
        self.evidence_index = self.value_index(val)
    
    def get_evidence(self):
        return self.dom[self.evidence_index]
    
    def set_assignment(self, val) -> None:
        """Set this variable's assignment value for factor lookups"""
        self.assignment_index = self.value_index(val)
    
    def get_assignment(self) -> None:
        return self.dom[self.assignment_index]
    
    # These routines are special low-level routines used directly by the
    # factor objects
    def set_assignment_index(self, index: int) -> None:
        """This routine is used by the factor objects"""
        self.assignment_index = index
    
    def get_assignment_index(self) -> int:
        """This routine is used by the factor objects"""
        return self.assignment_index
    
    def __repr__(self) -> str:
        """string to return when evaluating the object"""
        return "{}".format(self.name)
    
    def __str__(self) -> str:
        """more elaborate string for printing"""
        return "{}, Dom = {}".format(self.name, self.dom)


class Factor:
    """Class for defining factors. A factor is a function that is over
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

    Note that if the factor's scope is empty it is a constraint factor
    that stores only one value. add_values would be passed something
    like [[0.25]] to set the factor's single value. The get_value
    functions will still work.  E.g., get_value([]) will return the
    factor's single value. Constraint factors might be created when a
    factor is restricted."""
    
    def __init__(self, name: str, scope: List[Variable]):
        """create a Factor object, specify the Factor name (a string)
        and its scope (an ORDERED list of variable objects)."""
        self.scope = list(scope)
        self.name = name
        size = 1
        for v in scope:
            size = size * v.domain_size()
        self.values = [0] * size  # initialize values to be long list of zeros.
    
    def get_scope(self) -> List[Variable]:
        """returns copy of scope...you can modify this copy without affecting
           the factor object"""
        return list(self.scope)
    
    def add_values(self, values: List[list]) -> None:
        """This routine can be used to initialize the factor. We pass
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
         (A=2,B=b,C='light) is 2.25"""
        
        for t in values:
            index = 0
            for v in self.scope:
                index = index * v.domain_size() + v.value_index(t[0])
                t = t[1:]
            self.values[index] = t[0]
    
    def add_value_at_current_assignment(self, number: int) -> None:
        """This function allows adding values to the factor in a way
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
        the value 0.33 on the assignments (A=1, B='1', C='heavy')
        This has the same effect as the call
        add_values([1, 'a', 'heavy', 0.33])

        One advantage of the current_assignment interface to factor values is
        that we don't have to worry about the order of the variables in the
        factor's scope. add_values on the other hand has to be given tuples
        of values where the values must be given in the same order as the
        variables in the factor's scope.

        See recursive_print_values called by print_table to see an example of
        where the current_assignment interface to the factor values comes in
        handy.
        """
        
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        self.values[index] = number
    
    def get_value(self, variable_values: list):
        """This function is used to retrieve a value from the
        factor. We pass it an ordered list of values, one for every
        variable in self.scope. It then returns the factor's value on
        that set of assignments.  For example, if self.scope = [A, B,
        C], and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
        C.domain() = ['heavy', 'light'], and we invoke this function
        on the list [1, 'b', 'heavy'] we would get a return value
        equal to the value of this factor on the assignment (A=1,
        B='b', C='light')"""
        
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.value_index(variable_values[0])
            variable_values = variable_values[1:]
        return self.values[index]
    
    def get_value_at_current_assignments(self):
        """This function is used to retrieve a value from the
        factor. The value retrieved is the value of the factor when
        evaluated at the current assignment to the variables in its
        scope.

        For example, if self.scope = [A, B, C], and A.domain() =
        [1,2,3], B.domain() = ['a', 'b'], and C.domain() = ['heavy',
        'light'], and we had previously invoked A.set_assignment(1),
        B.set_assignment('a') and C.set_assignment('heavy'), then this
        function would return the value of the factor on the
        assignments (A=1, B='1', C='heavy')"""
        
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        return self.values[index]
    
    def print_table(self) -> None:
        """print the factor's table"""
        saved_values = []  # save and then restore the variable assigned values.
        for v in self.scope:
            saved_values.append(v.get_assignment_index())
        
        self.recursive_print_values(self.scope)
        
        for v in self.scope:
            v.set_assignment_index(saved_values[0])
            saved_values = saved_values[1:]
    
    def recursive_print_values(self, variables: List[Variable]) -> None:
        if len(variables) == 0:
            print("[", end=""),
            for v in self.scope:
                print("{} = {},".format(v.name, v.get_assignment()), end="")
            print("] = {}".format(self.get_value_at_current_assignments()))
        else:
            for val in variables[0].domain():
                variables[0].set_assignment(val)
                self.recursive_print_values(variables[1:])
    
    def __repr__(self) -> str:
        return "{}".format(self.name)


class BN:
    """Class for defining a Bayes Net. This class is simple, it just is a
    wrapper for a list of factors. And it also keeps track of all variables
    in the scopes of these factors """
    
    def __init__(self, name: str, variables: List[Variable],
                 factors: List[Factor]):
        self.name = name
        self.Variables = list(variables)
        self.Factors = list(factors)
        for f in self.Factors:
            for v in f.get_scope():
                if v not in self.Variables:
                    print("Bayes net initialization error")
                    print("Factor scope {} has variable {} that", end='')
                    print(" does not appear in list of variables {}.".format(
                        list(map(lambda x: x.name, f.get_scope())), v.name,
                        list(map(lambda x: x.name, variables))))
    
    def factors(self) -> List[Factor]:
        return list(self.Factors)
    
    def variables(self) -> List[Variable]:
        return list(self.Variables)


def get_variable_values(variables: List[Variable], values: list,
                        factor: Factor) -> list:
    temp = {}
    for variable in variables:
        if variable in factor.get_scope():
            temp[variable] = values[variables.index(variable)]
    values = []
    for variable in factor.get_scope():
        for var, value in temp.items():
            if var == variable:
                values.append(value)
    return values


def multiply_factors(factors: List[Factor]) -> Factor:
    """return a new factor that is the product of the factors in Factors"""
    variables = []
    for factor in factors:
        variables.extend(factor.get_scope())
    variables = list(set(variables))
    domains = [variable.domain() for variable in variables]
    values = []
    for tv in product(*domains):
        value, temp = 1, list(tv)
        for factor in factors:
            value *= factor.get_value(
                get_variable_values(variables, temp, factor)
            )
        values.append(temp + [value])
    f = Factor("Π({0})".format(factors), variables)
    f.add_values(values)
    return f


def restrict_factor(f: Factor, var: Variable, value) -> Factor:
    """f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor"""
    variables = [variable for variable in f.get_scope() if variable != var]
    domains = [variable.domain() if variable != var else [value]
               for variable in f.get_scope()]
    index = f.get_scope().index(var) if var in f.get_scope() else -1
    values = []
    for tv in product(*domains):
        temp = list(tv)
        value = f.get_value(temp)
        if index != -1:
            temp.pop(index)
        values.append(temp + [value])
    f = Factor("({0})/Γ({1}@{2})".format(f.name, var.name, value), variables)
    f.add_values(values)
    return f


def sum_out_variable(f: Factor, var: Variable) -> Factor:
    """return a new factor that is the product of the factors in Factors
       followed by the summing out of Var"""
    variables = [variable for variable in f.get_scope() if variable != var]
    domain = [variable.domain() for variable in f.get_scope()
              if variable != var]
    index = f.get_scope().index(var)
    values = []
    for tv in product(*domain):
        value, temp = 0, list(tv)
        for v in var.domain():
            temp.insert(index, v)
            value += f.get_value(temp)
            temp.pop(index)
        values.append(temp + [value])
    f = Factor("({0})/Σ({1})".format(f.name, var.name), variables)
    f.add_values(values)
    return f


def normalize(nums: List[float]) -> List[float]:
    """take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers"""
    s = sum(nums)
    return [num/s if s != 0 else 0 for num in nums]


# Orderings
def min_fill_ordering(factors: List[Factor], query_var: Variable) \
        -> List[Variable]:
    """Compute a min fill ordering given a list of factors. Return a list
    of variables from the scopes of the factors in Factors. The QueryVar is
    NOT part of the returned ordering"""
    scopes = []
    for f in factors:
        scopes.append(list(f.get_scope()))
    variables = []
    for s in scopes:
        for v in s:
            if v not in variables and v != query_var:
                variables.append(v)
    
    ordering = []
    while variables:
        (var, new_scope) = min_fill_var(scopes, variables)
        ordering.append(var)
        if var in variables:
            variables.remove(var)
        scopes = remove_var(var, new_scope, scopes)
    return ordering


def min_fill_var(scopes: List[List[Variable]], variables: List[Variable]) \
        -> Tuple[Variable, List[Variable]]:
    """Given a set of scopes (lists of lists of variables) compute and
    return the variable with minimum fill in. That the variable that
    generates a factor of smallest scope when eliminated from the set
    of scopes. Also return the new scope generated from eliminating
    that variable."""
    min_v = variables[0]
    (min_fill, min_new_scope) = compute_fill(scopes, variables[0])
    for v in variables[1:]:
        (fill, new_scope) = compute_fill(scopes, v)
        if fill < min_fill:
            min_v = v
            min_fill = fill
            min_new_scope = new_scope
    return min_v, min_new_scope


def compute_fill(scopes: List[List[Variable]], var: Variable) \
        -> Tuple[int, List[Variable]]:
    """Return the fill in scope generated by eliminating var from
    scopes along with the size of this new scope"""
    union = []
    for s in scopes:
        if var in s:
            for v in s:
                if v not in union:
                    union.append(v)
    if var in union:
        union.remove(var)
    return len(union), union


def remove_var(var: Variable, new_scope: List[Variable],
               scopes: List[List[Variable]]) -> List[List[Variable]]:
    """Return the new set of scopes that arise from eliminating var
    from scopes"""
    new_scopes = []
    for s in scopes:
        if var not in s:
            new_scopes.append(s)
    new_scopes.append(new_scope)
    return new_scopes


def VE(net: BN, query_var: Variable, evidence_vars: List[Variable]) \
        -> List[float]:
    """
    Input: Net---a BN object (a Bayes Net)
           QueryVar---a Variable object (the variable whose distribution
                      we want to compute)
           EvidenceVars---a LIST of Variable objects. Each of these
                          variables has had its evidence set to a particular
                          value from its domain using set_evidence.
    VE returns a distribution over the values of QueryVar, i.e., a list
    of numbers one for every value in QueryVar's domain. These numbers
    sum to one, and the ith number is the probability that QueryVar is
    equal to its ith value given the setting of the evidence
    variables. For example if QueryVar = A with Dom[A] = ['a', 'b',
    'c'], EvidenceVars = [B, C], and we have previously called
    B.set_evidence(1) and C.set_evidence('c'), then VE would return a
    list of three numbers. E.g. [0.5, 0.24, 0.26]. These numbers would
    mean that Pr(A='a'|B=1, C='c') = 0.5 Pr(A='a'|B=1, C='c') = 0.24
    Pr(A='a'|B=1, C='c') = 0.26
    """
    factors = []
    for factor in net.factors():
        temp = [variable for variable in evidence_vars
                if variable in factor.get_scope()]
        f = factor
        for variable in temp:
            f = restrict_factor(f, variable, variable.get_evidence())
        factors.append(f)
    
    variables = min_fill_ordering(factors, query_var)
    for variable in variables:
        temp = [factor for factor in factors if variable in factor.get_scope()]
        f = sum_out_variable(multiply_factors(temp), variable)
        for factor in temp:
            factors.remove(factor)
        factors.append(f)
    
    dist = []
    for variable in query_var.domain():
        value = multiply_factors(factors).get_value([variable])
        dist.append(value)
    
    return normalize(dist)


if __name__ == '__main__':
    pass
