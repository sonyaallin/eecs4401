from bnetbase import Variable, Factor, BN, adultDatasetBN
from typing import List
import itertools
import numpy as np
import csv

# https://stackoverflow.com/questions/17236486/calling-itertools-product-with-unkown-number-of-args was used to see how
# to use itertools.product with an unknwon amount of arguments.

def multiply_factors(Factors: List[Factor]):
    '''return a new factor that is the product of the factors in Fators
    @return a factor'''
    variables, keys, values, old_values, unique_domain, new_values, total_variables = [], [], [], [], [], [], []
    name = ""
    constant = []
    for factor in Factors:
        domains = []
        factor_values = {}
        
        # Get name of new factor
        if factor == Factors[-1]:
            name += factor.name
        else:
            name += f"{factor.name} * "
        
        if not factor.get_scope():
            constant.append(factor)
            continue
        
        # Get unique variables and domains
        for variable in factor.get_scope():
            if variable not in variables:
                variables.append(variable)
            total_variables.append(variable)

            domain = variable.domain()
            if domain not in unique_domain:
                unique_domain.append(domain)
            domains.append(domain)

        # Get each value in the factor
        for value in itertools.product(*domains):
            factor_values[value] = factor.get_value(value)

        old_values.append(factor_values)

    new_factor = Factor(name, variables)
    unique_variables = set(total_variables)
    indexes = [total_variables.index(var) for var in unique_variables]
    indexes.sort()

    # Get keys and values
    for i in old_values:
        keys.append(list(i.keys()))
        values.append(list(i.values()))
    
    # Get all keys and values of new factor
    for key, value in zip(itertools.product(*keys), itertools.product(*values)):
        new_value = 1
        new_key = []
        for k, v in zip(key, value):
            new_key.extend(k[0:])
            new_value *= v
        
        # Check if key has contradictory elements such as s and -s at the same time
        contra = False
        for domain in unique_domain:
            count = 0
            for val in domain:
                if val in new_key:
                    count += 1
                if count > 1:
                    contra = True
                    break
            if contra:
                break
        
        if contra:
            continue

        # Remove any repeated elemented such as 's' occuring twice
        final_key = [new_key[index] for index in indexes]

        full = final_key + [new_value]
        new_values.append(full)

    new_factor.add_values(new_values)

    for c in constant:
        new_factor.values = list(np.array(new_factor.values) * c.get_value_at_current_assignments())

    return new_factor


def restrict_factor(f: Factor, var: Variable, value: any):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor
    @return a factor'''
    domains = []
    variables = []
    new_values = []
    index = -1

    for i, variable in enumerate(f.get_scope()):
        if variable != var:
            variables.append(variable)
            domains.append(variable.domain())   
        else:
            index = i
            domains.append([value])

    new_factor = Factor(f.name, variables)
    
    for settings in itertools.product(*domains):
        assignments = list(settings)
        assignments.pop(index)
        full = assignments + [f.get_value(settings)]
        new_values.append(full)
        
    new_factor.add_values(new_values)
    return new_factor


def sum_out_variable(f: Factor, var: Variable):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var
    @return a factor'''
    variables = []
    domains = []
    factor_values = {}
    new_values = {}
    index = -1

    if f.get_scope()[-1] == var:
        name = f.name.replace(f",{var.name}", "")
    else:
        name = f.name.replace(f"{var.name},", "")
    
    
    for i, variable in enumerate(f.get_scope()):
        if variable != var:
            variables.append(variable)
        else:
            index = i
        domains.append(variable.domain())
    
    new_factor = Factor(name, variables)
    
    for value in itertools.product(*domains):
        factor_values[value] = f.get_value(value)
    
    for ks in factor_values.keys():
        new_ks = list(ks)
        new_ks.pop(index)
        new_values[tuple(new_ks)] = new_values.get(tuple(new_ks), 0) + factor_values[ks]
    
    for (k, v) in new_values.items():
        new_factor.add_values([list(k) + [v]])
        
    return new_factor


def normalize(nums: List[int]):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers
    @return a normalized list of numbers'''
    if sum(nums) != 0:
        return nums / np.sum(nums)
    else:
        return np.array(nums) + 1/len(nums)


def min_fill_ordering(Factors: List[Factor], QueryVar: Variable):
    '''Compute an elimination order given a list of factors using the min fill heuristic. 
    Variables in the list will be derived from the scopes of the factors in Factors. 
    Order the list such that the first variable in the list generates the smallest
    factor upon elimination. The QueryVar must NOT part of the returned ordering using.
    @return a list of variables'''
    variables = []
    
    for f in Factors:
        variables.extend(f.get_scope())
    
    variables = list(set(variables))
    variables.remove(QueryVar)
    counts = [0] * len(variables)
    
    for i, var in enumerate(variables):
        count = []
        for f in Factors:
            if var in f.get_scope():
                count.extend(f.get_scope())
        
        count = list(set(count))
        counts[i] = len(count) - 1
        
    return [variables[i] for i in np.argsort(counts)]

###


def VE(Net: BN, QueryVar: Variable, EvidenceVars: List[Variable]):
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
    factors = Net.factors()
    
    for i in range(len(factors)):
        factor = factors[i]
        for var in EvidenceVars:
            if var in factors[i].get_scope():
                factor = restrict_factor(factor, var, var.get_evidence())
        factors[i] = factor

    variables = min_fill_ordering(factors, QueryVar)
    
    while variables:
        var = variables.pop(0)
        m_factors = []

        for f in factors:
            if var in f.get_scope():
                m_factors.append(f)
        new = multiply_factors(m_factors)
        final = sum_out_variable(new, var)

        for f in m_factors:
            factors.remove(f)
        factors.append(final)
        
    return normalize(multiply_factors(factors).values)


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
    # READ IN THE DATA
    input_data = []
    with open('data/adult-dataset.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None)  # skip header row
        for row in reader:
            input_data.append(row)

    # DOMAIN INFORMATION REFLECTS ORDER OF COLUMNS IN THE DATA SET
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
    total = len(input_data)
    variables = []
    factors = []
    values = {}
    rows_to_values = {0:"Work", 1:"Education", 2:"MaritalStatus", 3:"Occupation", 4:"Relationship", 5:"Race", 6:"Gender", 7:"Country", 8:"Salary"}
    
    for key, val in variable_domains.items():
        variables.append(Variable(key, val))
        values[key] = [[0,0] for _ in range(len(val))]
    
    for row in input_data:
        for index, item in enumerate(row):                
            key = rows_to_values[index]
            index = variable_domains[key].index(item)
        
            if row[-1] != "<50K":
                values[key][index][1] = values[key][index][1] + 1
            else:
                values[key][index][0] = values[key][index][0] + 1

    factors.append(Factor("P(Salary)", [variables[-1]]))
    factors[0].add_values([["<50K", (values['Salary'][0][0])/total], [">=50K", (values['Salary'][1][1])/total]])
    
    for variable in variables[:-1]:
        factors.append(Factor(f"P({variable.name}|Salary)", [variable, variables[-1]]))
        factor_values = []
        
        for index, val in enumerate(variable.domain()):
            for i in range(2):
                var_val = (values[variable.name][index][i])/(values['Salary'][i][i])
                factor_values.append([val, variables[-1].domain()[i], var_val])

        factors[-1].add_values(factor_values)
        
    return BN("Naive Bayes Model on Training Data Set", variables, factors)


def explore(Net: BN, question: int):
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
    num = 0
    count = 0
    
    input_data = []
    with open('data/test-data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None)  # skip header row
        for row in reader:
            input_data.append(row)
    
    rows_to_values = {0:"Work", 1:"Education", 2:"MaritalStatus", 3:"Occupation", 4:"Relationship", 5:"Race", 6:"Gender", 7:"Country", 8:"Salary"}
    
    E1 = []
    
    for i in [0, 1, 3, 4]:
        var = Net.get_variable(rows_to_values[i])
        E1.append(var)
    
    for row in input_data:
        if question % 2 == 0 and row[6] != 'Male':
            continue
        if question % 2 != 0 and row[6] == 'Male':
            continue
        
        E1[0].set_evidence(row[0])
        E1[1].set_evidence(row[1])
        E1[2].set_evidence(row[3])
        E1[3].set_evidence(row[4])

        salary = Net.get_variable("Salary")
        probsE1 = VE(Net, salary, E1)[1]
        
        if question in [5, 6]:
            if probsE1 > 0.5:
                count += 1
            num += 1
        elif question in [3, 4]:
            if probsE1 > 0.5:
                if row[8] == '>=50K':
                    count += 1
                num += 1
        elif question in [1, 2]:
            E2 = E1.copy()
            E2.append(Net.get_variable(rows_to_values[6]))
            E2[4].set_evidence(row[6])
            probsE2 = VE(Net, salary, E2)[1]
            if probsE1 > probsE2:
                count += 1
            num += 1
            
    
    return count/num * 100
            
    
