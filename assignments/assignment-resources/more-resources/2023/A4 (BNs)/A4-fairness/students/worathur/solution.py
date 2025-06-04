from bnetbase import Variable, Factor, BN, adultDatasetBN
from itertools import product
from collections import defaultdict
import csv

def equal_at_indices(lst1, lst2, common_indices):

    for i, j in common_indices:
        if lst1[i] != lst2[j]:
            return False
    return True

def pop_at_indices(lst, indices):

    return [lst[i] for i in range(len(lst)) if i not in indices]

def zip_vars_to_vals(vars, vals):

    for var, val in zip(vars, vals):
        var.set_assignment(val)


def multiply_factors(factors):
    """return a new factor that is the product of the factors in Factors
    @return a factor

    """

    if len(factors) == 1:
        return factors[0]

    if len(factors) > 2:
        prod_rest_factor = multiply_factors(factors[1:])
        return multiply_factors([factors[0], prod_rest_factor])


    f0, f1 = factors[0], factors[1]
    common_vars = list(set(f0.get_scope()).intersection(set(f1.get_scope())))
    common_indices = [(f0.get_scope().index(var), f1.get_scope().index(var)) for var in common_vars]

    # List of all rows from f0, f1
    f0_assignments = list(product(*tuple([var.domain() for var in f0.get_scope()])))
    f1_assignments = list(product(*tuple([var.domain() for var in f1.get_scope()])))

    # Get all pairs of variable assignments from f0 and f1 which agree on common variables
    assignment_pairs = filter(lambda lst_pair: equal_at_indices(lst_pair[0], lst_pair[1], common_indices),
                              list(product(f0_assignments, f1_assignments)))

    prod_assignments = []
    for assign1, assign2 in assignment_pairs:
        assign1, assign2 = list(assign1), list(assign2)
        # Remove occurrences of common variables from factor1 assignments to avoid duplicates in result row
        prod_assignment = assign1 + pop_at_indices(assign2, [common_index[1] for common_index in common_indices])
        prod_assignments.append((assign1, assign2, prod_assignment))

    values = []

    for f0_assignment, f1_assignment, prod_assignment in prod_assignments:
        # Append the product of probabilities to the product assignment to obtain a factor table entry
        prod_assignment.append(f0.get_value(f0_assignment) * f1.get_value(f1_assignment))
        values.append(prod_assignment)

    # Remove occurrences of common variables from factor1 scope to avoid duplicate variables in scope
    prod_scope = f0.get_scope() + pop_at_indices(f1.get_scope(),
                                                 [common_index[1] for common_index in common_indices])
    prod_name = "({} x {})".format(f0.name, f1.name)
    prod_factor = Factor(prod_name, prod_scope)

    prod_factor.add_values(values)

    return prod_factor


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor
    @return a factor'''

    # index of restricted variable in scope
    restrict_index = f.get_scope().index(var)

    # Get all assignments in which var=value
    f_assignments = list(product(*tuple([scope_var.domain() if scope_var != var else [value]
                                              for scope_var in f.get_scope()])))

    values = []
    for assignment in f_assignments:
        assignment = list(assignment)
        prob_val = f.get_value(assignment)
        assignment.pop(restrict_index)
        assignment.append(prob_val)
        values.append(assignment)

    restrict_scope = f.get_scope()
    restrict_scope.pop(restrict_index)

    restrict_name = "{}[{} = {}]".format(f, repr(var), value)
    restrict_factor = Factor(restrict_name, restrict_scope)
    restrict_factor.add_values(values)

    return restrict_factor

def restrict_factor_to_evidence(f, evidence_vars):

    restricted_factor = f
    for var, val in evidence_vars:
        if var in restricted_factor.get_scope():
            restricted_factor = restrict_factor(restricted_factor, var, val)
    return restricted_factor

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the summing out of Var
    @return a factor'''       
    ### YOUR CODE HERE ###
    sum_var_index = f.get_scope().index(var)

    # variables which will remain unassigned after summing out var
    rem_vars = f.get_scope()
    rem_vars.pop(sum_var_index)

    marginal_assignments = list(product(*[rem_var.domain() for rem_var in rem_vars]))

    values = []
    for assignment in marginal_assignments:

        prob_sum = 0
        assignment = list(assignment)

        zip_vars_to_vals(rem_vars, assignment)

        for val in var.domain():
            var.set_assignment(val)
            prob_sum += f.get_value_at_current_assignments()

        assignment.append(prob_sum)
        values.append(assignment)

    marginal_scope = rem_vars
    marginal_name =  "(SUM_{} [{}])".format(repr(var), f)

    marginal_factor = Factor(marginal_name, marginal_scope)
    marginal_factor.add_values(values)

    return marginal_factor


def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers
    @return a normalized list of numbers'''
    ### YOUR CODE HERE ###

    res = []
    normalizing_constant = sum(nums)
    for num in nums:
        res.append(num / normalizing_constant)

    return res

def factor_size_after_elim(hypergraph, var):
    """Return the size of the new hyperedge obtained by taking the union
       over all hyperedges over var to be elimnated.
    """
    assoc_vars = set()
    for he in hypergraph:
        if var in he:
            assoc_vars |= he
    assoc_vars.remove(var)
    return len(assoc_vars)


def min_fill_ordering(factors, query_var):
    '''Compute an elimination order given a list of factors using the min fill heuristic. 
    Variables in the list will be derived from the scopes of the factors in Factors. 
    Order the list such that the first variable in the list generates the smallest
    factor upon elimination. The QueryVar must NOT part of the returned ordering using.
    @return a list of variables''' 
    ### YOUR CODE HERE ###

    min_fill_order = []

    vars = set()
    hypergraph = []
    for factor in factors:
        vars = vars.union(set(factor.get_scope()))
        hypergraph.append(set(factor.get_scope()))

    vars.remove(query_var)

    while len(vars) > 0:

        elim_var = min(vars, key=lambda var: factor_size_after_elim(hypergraph, var))
        assoc_vars = set()
        new_hypergraph = []
        for i, he in enumerate(hypergraph):
            if elim_var in he:
                assoc_vars |= he
            else:
                new_hypergraph.append(he)

        assoc_vars.remove(elim_var)
        vars.remove(elim_var)
        new_hypergraph.append(assoc_vars)
        min_fill_order.append(elim_var)
        hypergraph = new_hypergraph

    return min_fill_order

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
    @return a list of probabilities, one for each item in the domain of the QueryVar'''

    # Restrict the CPT's to evidence to obtain initial factors
    init_factors = []
    for factor in Net.factors():
        restricted_factor = restrict_factor_to_evidence(factor, zip(EvidenceVars, [var.get_evidence() for var in EvidenceVars]))
        init_factors.append(restricted_factor)

    # Use min_fill heuristic to choose elimination order
    elim_order = min_fill_ordering(Net.factors(), QueryVar)

    # buckets is a mapping of variables to a list of factors in which the variable appears
    buckets = {k: [] for k in Net.variables()}
    elim_order.append(QueryVar)

    for factor in init_factors:
        for var in elim_order:
            if var in factor.get_scope():
                buckets[var].append(factor)
                break

    for i in range(len(elim_order) - 1):
        var = elim_order[i]

        if not buckets[var]:
            continue

        prod_factor = multiply_factors(buckets[var])
        marginal_factor = sum_out_variable(prod_factor, var)
        j = i + 1
        while j < len(elim_order):
            if elim_order[j] in marginal_factor.get_scope():
                buckets[elim_order[j]].append(marginal_factor)
                break
            j += 1

    # At this point, all factors are in the bucket of QueryVar, and depend only on QueryVar
    prod_factor = multiply_factors(buckets[QueryVar])

    query_var_distribution = []

    for val in QueryVar.domain():
        QueryVar.set_assignment(val)
        query_var_distribution.append(prod_factor.get_value_at_current_assignments())

    return normalize(query_var_distribution)


def NaiveBayesModel():
    '''
   NaiveBayesModel returns a BN that is a Naive Bayes model that 
   represents the joint distribution of value assignments to 
   variables in the Adult Dataset from UCI.  Remember a Naive Bayes model
   assumes P(X1, X2,.... XN, Class) can be represented as 
   P(X1|Class)*P(X2|Class)* .... *P(XN|Class)*P(Class).
   When you generated your Bayes Net, assume that the values 
   in the SALARY column of the dataset are the CLASS that we want to predict.
   @return a BN that is a Naive Bayes model and which represents the Adult Dataset. 
    '''
    ### READ IN THE DATA
    input_data = []
    with open('data/adult-dataset.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)

    ### DOMAIN INFORMATION REFLECTS ORDER OF COLUMNS IN THE DATA SET
    variable_domains = {
    "MaritalStatus": ['Not-Married', 'Married', 'Separated', 'Widowed'],
    "Relationship": ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
    "Race": ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'],
    "Gender": ['Male', 'Female'],
    "Occupation": ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'],
    "Country": ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'],
    "Education": ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'],
    "Work": ['Not Working', 'Government', 'Private', 'Self-emp'],
    "Salary": ['<50K', '>=50K']
    }
    ### YOUR CODE HERE ###
    name_to_var = {}
    # Initialize variables
    for name, domain in variable_domains.items():
        var = Variable(name, domain)
        name_to_var[name] = var

    salary_var = name_to_var["Salary"]
    prior_dist = Factor('P(Salary)', [salary_var])


    bn_factors = [prior_dist]

    # Initialize prior distribution
    for val in salary_var.domain():
        salary_var.set_assignment(val)
        prob_val = [row[headers.index("Salary")] for row in input_data].count(val) / len(input_data)
        prior_dist.add_value_at_current_assignment(prob_val)



    for name, cond_var in name_to_var.items():
        if name == "Salary":
            continue

        cond_dist = Factor("P({}|Salary)".format(name), [cond_var, salary_var])
        assignments = list(product(salary_var.domain(), cond_var.domain()))

        for salary, outcome in assignments:
            salary_var.set_assignment(salary)
            cond_var.set_assignment(outcome)
            prob_joint = [(row[headers.index("Salary")], row[headers.index(name)]) for
                         row in input_data].count((salary, outcome)) / len(input_data)

            prob_cond = prob_joint / prior_dist.get_value_at_current_assignments()
            cond_dist.add_value_at_current_assignment(prob_cond)
        bn_factors.append(cond_dist)

    salary_bn = BN("Adult BN, Prior=Salary", list(name_to_var.values()), bn_factors)
    return salary_bn



def explore(Net, question):
    '''    Input: Net---a BN object (a Bayes Net)
           question---an integer indicating the question in HW4 to be calculated. Options are:
           1. What percentage of the women in the data set end up with a P(S=">=$50K"|E1) that is strictly greater than P(S=">=$50K"|E2)?
           2. What percentage of the men in the data set end up with a P(S=">=$50K"|E1) that is strictly greater than P(S=">=$50K"|E2)?
           3. What percentage of the women in the data set with P(S=">=$50K"|E1) > 0.5 actually have a salary over $50K?
           4. What percentage of the men in the data set with P(S=">=$50K"|E1) > 0.5 actually have a salary over $50K?
           5. What percentage of the women in the data set are assigned a P(Salary=">=$50K"|E1) > 0.5, overall?
           6. What percentage of the men in the data set are assigned a P(Salary=">=$50K"|E1) > 0.5, overall?
           @return a percentage (between 0 and 100)
    '''

    input_data = []
    with open('data/test-data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None)  # skip header row
        for row in reader:
            input_data.append(row)

    e1 = {"Work", "Occupation", "Education", "Relationship"}
    e2 = e1.union({"Gender"})

    name_to_vars = {name : list(filter(lambda x: x.name == name, Net.variables()))[0] for name in e2.union({"Salary"})}
    salary_var = name_to_vars["Salary"]
    outcome_indices = { value: salary_var.domain().index(value) for value in salary_var.domain()}
    answer, prob_given_e1, prob_given_e2 = 0, None, None

    gender = "Male" if question % 2 == 0 else "Female"
    input_data = list(filter(lambda x: x[headers.index("Gender")] == gender, input_data))


    if question in [1, 2]:

        for row in input_data:
            for label in e2:
                name_to_vars[label].set_evidence(row[headers.index(label)])

            prob_given_e1 = VE(Net, name_to_vars["Salary"],
                               [name_to_vars[name] for name in e1])[outcome_indices[">=50K"]]
            prob_given_e2 = VE(Net, name_to_vars["Salary"],
                               [name_to_vars[name] for name in e2])[outcome_indices[">=50K"]]
            if prob_given_e1 > prob_given_e2:
                answer += 1

        answer /= len(input_data)

    elif question in [3, 4]:
        total = 0

        for row in input_data:

            for label in e2:
                name_to_vars[label].set_evidence(row[headers.index(label)])

            prob_given_e1 = VE(Net, name_to_vars["Salary"],
                               [name_to_vars[name] for name in e1])[outcome_indices[">=50K"]]
            if prob_given_e1 > 0.5:
                total += 1

                if row[headers.index("Salary")] == ">=50K":
                    answer += 1

        answer /= total

    elif question in [5, 6]:

        for row in input_data:

            for label in e2:
                name_to_vars[label].set_evidence(row[headers.index(label)])

            prob_given_e1 = VE(Net, name_to_vars["Salary"],
                               [name_to_vars[name] for name in e1])[outcome_indices[">=50K"]]
            if prob_given_e1 > 0.5:
                answer += 1

        answer /= len(input_data)


    return int(answer * 100)


if __name__ == '__main__':
    bnet = NaiveBayesModel()

    print(explore(bnet, 1))
    print(explore(bnet, 2))
    print(explore(bnet, 3))
    print(explore(bnet, 4))
    print(explore(bnet, 5))
    print(explore(bnet, 6))







