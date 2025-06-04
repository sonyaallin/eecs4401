from bnetbase import Variable, Factor, BN
import csv
import itertools

def multiply_factors(Factors):
    '''Factors is a list of factor objects.
    Return a new factor that is the product of the factors in Factors.
    @return a factor''' 
    ### YOUR CODE HERE ###
    # Define the scope of the new factor
    # Factors = [Factors[1]]
    variables = []
    var_length = []
    for factor in Factors:
        var_length.append(len(factor.scope))
        for var in factor.scope:
            variables.append(var)
    result_variable = []
    for var in variables:
        if var not in result_variable:
            result_variable.append(var)
            
    # print(variables)
    # print(var_length)
    # Define the name of the new factor
    name = 'P('
    if len(variables) == 1:
        name += variables[0].name + ')'
    else:
        for var in variables:
            name += var.name + ','
        name = name[:-1] + ')'
    # Create the new factot
    new_factor = Factor(name, result_variable)
    domains = []
    real_domains = []
    for var in variables:
        if var.domain() not in domains:
            real_domains.append(var.domain())
        domains.append(var.domain())
    fake_dom = []
    for fdom in itertools.product(*domains):
        fdom = list(fdom)
        fake_dom.append(fdom)
    # print(fake_dom)
    #print(real_domains): [['e', '-e'], ['s', '-s'], ['b', '-b']]
    #print(domains):[['e', '-e'], ['s', '-s'], ['e', '-e'], ['b', '-b']]
    new_doms = []
    counter = 0
    for doms in itertools.product(*real_domains):
        doms = list(doms)
        # print(doms)
        final_prob = 1
        for i in range(len(Factors)):
            # print(Factors[i])
            begin = sum(var_length[:i])
            end = sum(var_length[:i+1])
            # print(begin, end)
            # print(fake_dom[counter])
            # print(fake_dom[counter][begin:end])
            # print(Factors[i].get_value(fake_dom[counter][begin:end]))
            final_prob *= Factors[i].get_value(fake_dom[counter][begin:end])
            # print(final_prob)
        doms.append(final_prob)
        new_doms.append(doms)
        counter += 1
    # print(new_doms)
    new_factor.add_values(new_doms)
    # print(new_factor.values)
    return new_factor


#     new_doms, new_val = create_domians(Factors[0])
#     for i in range(1, len(Factors)):
#         another_doms, another_val = create_domians(Factors[i])
#         new_doms, new_val = multiply_2_factors(new_doms, another_doms, new_val, another_val)
#     new_factor.add_values(new_doms)
#     return new_factor

# def create_domians(factor):
#     # Given a factor creates the domains
#     variables = factor.scope
#     domains = []
#     for v in variables:
#         domains.append(v.domain())
#     new_doms = []
#     values = []
#     for doms in itertools.product(*domains):
#         doms = list(doms)
#         values.append(factor.get_value(doms))
#         new_doms.append(doms)
#     print(new_doms)
#     print(values)
#     return new_doms, values

# def multiply_2_factors(new_doms, another_doms, new_val, another_val):
#     # Given 2 domains multiplies them
#     print(new_doms)
#     print(another_doms)
#     for doms in [if itertools.product(*new_doms, *another_doms):
#         doms = list(doms)
#         print(doms)
#         # for res in itertools.product(*doms):
#         #     res = list(res)
#         #     print(res)
    





    # domains = []
    # real_domains = []
    # for var in variables:
    #     if var.domain() not in domains:
    #         real_domains.append(var.domain())
    #     domains.append(var.domain())

    # print(domains)
    # new_doms = []
    # for doms in itertools.product(*real_domains):
    #     doms = list(doms)
    #     print(len(doms))
    #     final_prob = 1
    #     for i in range(len(Factors)):
    #         print(Factors[i])
    #         # final_prob *= Factors[i].get_value(doms[])
    #     doms.append(final_prob)
    #     new_doms.append(doms)
    # new_factor.add_values(new_doms)
    # return new_factor

def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor.
    @return a factor''' 
    ### YOUR CODE HERE ###
    # If the factor has only one variable, return f
    # print("Restrict==================================")
    # print(f)
    # print(f.scope)
    # print(var)
    # print(value)
    # print(f.scope)
    # print("===========================================")
    if len(f.scope) == 1:
        return f
    # Define the scope of the new factor
    variables = []
    for v in f.scope:
        variables.append(v)
    # Define the name of the new factor
    # name = 'RESTRICT('
    # if len(variables) == 1:
    #     name += variables[0].name + '|' + var.name + '=' + value + ')'
    # else:
    #     for item in variables:
    #         name += item.name + ','
    #     name = name[:-1] + '|' + item.name + '=' + value + ')'
    # Create the new factot
    new_factor = Factor(f.name, variables)
    # Form the product of the factors
    domains = []
    # print(variables)
    for v in variables:
        # print(var)
        if v != var:
            # print(v.domain())
            domains.append(v.domain())
        else:
            for i in range(len(v.domain())):
                if v.domain()[i] == value:
                    domains.append([v.domain()[i]])
    # print(domains)
    # print(f.print_table)
    new_doms = []
    for doms in itertools.product(*domains):
        doms = list(doms)
        # f.get_value(['s', 'e'])
        doms.append(f.get_value(doms))
        new_doms.append(doms)
    new_factor.add_values(new_doms)
    return new_factor
   
def sum_out_variable(f, var):
    '''f is a factor, var is a Variable.
    Return a new factor that is the result of summing var out of f, by summing
    the function generated by the product over all values of var.
    @return a factor'''       
    ### YOUR CODE HERE ###
    # If the factor has only one variable, return f
    if len(f.scope) == 1:
        return f
    # Define the scope of the new factor
    variables = []
    used_variables = []
    for v in f.scope:
        variables.append(v)
        if v != var:
            used_variables.append(v)
    # Define the name of the new factor
    if not variables.index(var):
        return f
    used_index = variables.index(var)
    name = 'SUM('
    if len(variables) == 1:
        name += variables[0].name + ')'
    else:
        for var in variables:
            name += var.name + ','
        name = name[:-1] + ')'
    # Create the new factot
    new_factor = Factor(name, used_variables)
    # Form the product of the factors
    domains = []
    for var in variables:
        domains.append(var.domain())
    used_domains = []
    for var in used_variables:
        used_domains.append(var.domain())

    # print(variables)
    # print(used_variables)
    # print(used_domains)
    # print(used_index)
    # print(domains)
    result_dom = []
    for used_domain in itertools.product(*used_domains):
        used_domain = list(used_domain)
        result_dom.append(used_domain)
    
    new_doms = []
    for res in result_dom:
        result_porb = 0
        for dom in itertools.product(*domains):
            dom_copy = list(dom)
            # print(dom_copy)
            dom = list(dom)
            dom = dom[:used_index] + dom[used_index+1:]
            if res == dom:
                result_porb += f.get_value(dom_copy)
        res.append(result_porb)
        new_doms.append(res)
    new_factor.add_values(new_doms)
    return new_factor
             
def normalize(nums):
    '''num is a list of numbers. Return a new list of numbers where the new
    numbers sum to 1, i.e., normalize the input numbers.
    @return a normalized list of numbers'''
    ### YOUR CODE HERE ###
    total = len(nums)
    sum = 0
    for num in nums:
        sum += num
    if sum == 0:
        return nums
    for i in range(total):
        nums[i] /= sum
    return nums

def min_fill_ordering(Factors, QueryVar):
    '''Factors is a list of factor objects, QueryVar is a query variable.
    Compute an elimination order given list of factors using the min fill heuristic. 
    Variables in the list will be derived from the scopes of the factors in Factors. 
    Order the list such that the first variable in the list generates the smallest
    factor upon elimination. The QueryVar must NOT part of the returned ordering list.
    @return a list of variables''' 
    ### YOUR CODE HERE ###
    variables = []
    for factor in Factors:
        for var in factor.scope:
            if var not in variables:
                variables.append(var)
    counter = [0 for i in range(len(variables))]
    for factor in Factors:
        for var in factor.scope:
            if var == QueryVar:
                counter[variables.index(var)] += 1
    minimun = min(counter)
    maximun = max(counter)
    ordering = []
    # print(counter)
    while True:
        index = counter.index(minimun)
        counter[index] = maximun + 1
        ordering.append(variables[index])
        minimun = min(counter)
        if len(ordering) == len(variables):
            break
    ordering.remove(QueryVar)
    return ordering

def VE(Net, QueryVar, EvidenceVars):
    
    """
    Input: Net---a BN object (a Bayes Net)
           QueryVar---a Variable object (the variable whose distribution
                      we want to compute)
           EvidenceVars---a LIST of Variable objects. Each of these
                          variables has had its evidence set to a particular
                          value from its domain using set_evidence.
     VE returns a distribution over the values of QueryVar, i.e., a list
     of numbers, one for every value in QueryVar's domain. These numbers
     sum to one, and the i'th number is the probability that QueryVar is
     equal to its i'th value given the setting of the evidence
     variables. For example if QueryVar = A with Dom[A] = ['a', 'b',
     'c'], EvidenceVars = [B, C], and we have previously called
     B.set_evidence(1) and C.set_evidence('c'), then VE would return a
     list of three numbers. E.g. [0.5, 0.24, 0.26]. These numbers would
     mean that Pr(A='a'|B=1, C='c') = 0.5 Pr(A='b'|B=1, C='c') = 0.24
     Pr(A='c'|B=1, C='c') = 0.26
     @return a list of probabilities, one for each item in the domain of the QueryVar
     """
    ### YOUR CODE HERE ###

    # Get the factors
    factors = []
    for factor in Net.Factors:
        factors.append(factor)
    # print(factors)
    # Get the variables
    variables = []
    for factor in factors:
        for var in factor.scope:
            if var not in variables:
                variables.append(var)
    # print(variables)
    # Get the evidence variables
    # print(EvidenceVars)
    # for var in EvidenceVars:
    #     print(var.get_evidence())
    # Get the query variable
    # print(QueryVar)
    # Eliminate the variables
    # 1. Replace each factor f∈F that mentions a variable(s) in E with its restriction fE=e (this might yield a “constant” factor)
    # for factor in factors:
    #     print(factor.name)
    #     factor.print_table();
    # print('-----------------')
    for factor in factors:
        # print(factors)
        # print(factor)
        # print(index = factors.index(factor))
        index = factors.index(factor)
        for var in factor.scope:
            if var in EvidenceVars:
                factors[index] = restrict_factor(factor, var, var.get_evidence())
    # for factor in factors:
    #     print(factor.name)
    #     factor.print_table();

    # 2. For each Zj - in the order given - eliminate Zj ∈ Z as follows:
    ordering = min_fill_ordering(factors, QueryVar)
    # print(ordering)
    remaining = []
    for unused in ordering:
        if unused not in EvidenceVars:
            remaining.append(unused)
    # print(remaining)
    # print("=======")
    # 2.1 Compute new factor gj = ∑Zj f1 x f2 x ... x fk, where the fi are the factors in F that include Zj
    multiply = [] 
    gj = []
    for Zj in remaining:
        multiply = []
        # print(Zj)
        for factor in factors:
            if Zj in factor.scope:
                multiply.append(factor)
        # print(multiply)
        new_factor = multiply_factors(multiply)
        # print(new_factor, Zj)
        gj.append(sum_out_variable(new_factor, Zj))
    #     print()
    # for factor in gj:
    #     factor.print_table()
    #     print("===")

    # print("===")
    # print(summation)
    # for new_factor in summation:
    #     print(new_factor.values)
    #     # new_factor = sum_out_variable(new_factor, Zj)
    # gi = sum_out_variable()
    # 2.2 Remove the factors fi (that mention Zj) from F and add new factor gj to F
    pop_list = []
    for i in range(len(factors)):
        for each in factors[i].scope:
            if each in remaining:
                pop_list.append(i)
    # print(factors)
    factors = [i for j, i in enumerate(factors) if j not in pop_list]
    # print(factors)
    for factor in gj:
        factors.append(factor)
    # print(factors)
    # print("scop:")
    # for factor in factors:
    #     print(factor.scope)
    # 3. The remaining factors at the end of this process will refer only to the query variable Q. Take their product and normalize to produce P(Q|E).
    product = multiply_factors(factors)
    summing = sum_out_variable(product, QueryVar)
    result = []
    QueryVar.set_assignment(QueryVar.dom[0])
    summing.get_value_at_current_assignments()
    result.append(summing.get_value_at_current_assignments())
    QueryVar.set_assignment(QueryVar.dom[1])
    summing.get_value_at_current_assignments()
    # print(summing.print_table())
    result.append(summing.get_value_at_current_assignments())
    # print("resss1:")
    # print(result)
    result = normalize(result)
    # print("resss:")
    # print(result)
    return result

    
    # resutl[0] = normalize(product.get_values)
    # print(product)
    # norm = normalize(product)
    # return norm

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
    "Work": ['Not Working', 'Government', 'Private', 'Self-emp'],
    "Education": ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'],    
    "Occupation": ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'],    
    "MaritalStatus": ['Not-Married', 'Married', 'Separated', 'Widowed'],
    "Relationship": ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
    "Race": ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'],
    "Gender": ['Male', 'Female'],
    "Country": ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'],
    "Salary": ['<50K', '>=50K']
    }
    ### YOUR CODE HERE ###
    # 1. define name of BN
    name = "Naive Bayes Model"
    # 2. define variables
    variables = []
    work = Variable("Work", ['Not Working', 'Government', 'Private', 'Self-emp'])
    education = Variable("Education", ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'])
    occupation = Variable("Occupation", ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'])
    marital_status = Variable("MaritalStatus", ['Not-Married', 'Married', 'Separated', 'Widowed'])
    relationship = Variable("Relationship", ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'])
    race = Variable("Race", ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'])
    gender = Variable("Gender", ['Male', 'Female'])
    country = Variable("Country", ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'])
    salary = Variable("Salary", ['<50K', '>=50K'])
    variables.append(work)
    variables.append(education)
    variables.append(occupation)
    variables.append(marital_status)
    variables.append(relationship)
    variables.append(race)
    variables.append(gender)
    variables.append(country)
    variables.append(salary)
    # 3. define factors
    factors = []
    # Use "Salary" as a prior for your model
    Fsalary = Factor("Salary", [salary])
    #  and condition all of the other variables on "Salary".  We will use this model to make predictions of income in the next section.
    Fwork = Factor("P(Salary|Work)", [work, salary])
    Fedu = Factor("P(Salary|Education)", [education, salary])
    Focc = Factor("P(Salary|Occupation)", [occupation, salary])
    Fmar = Factor("P(Salary|MaritalStatus)", [marital_status, salary])
    Frel = Factor("P(Salary|Relationship)", [relationship, salary])
    Frac = Factor("P(Salary|Race)", [race, salary])
    Fgen = Factor("P(Salary|Gender)", [gender, salary])
    Fcou = Factor("P(Salary|Country)", [country, salary])
    factors.append(Fsalary)
    factors.append(Fwork)
    factors.append(Fedu)
    factors.append(Focc)
    factors.append(Fmar)
    factors.append(Frel)
    factors.append(Frac)
    factors.append(Fgen)
    factors.append(Fcou)
    # 4. define the conditional probability tables for each factor
    positive_salary = 0
    negative_salary = 0
    for data in input_data:
        if (data[-1] == "<50K"):
            negative_salary += 1
        else:
            positive_salary += 1
    total = positive_salary + negative_salary
    Fsalary.add_values([['<50K', negative_salary/total], ['>=50K', positive_salary/total]])
    # read other data
    not_working_negative = 0
    government_negative = 0
    private_negative = 0
    self_emp_negative = 0
    # work 
    for data in input_data:
        if (data[0] == "Not Working" and data[-1] == "<50K"):
            not_working_negative += 1
        elif (data[0] == "Government" and data[-1] == "<50K"):
            government_negative += 1
        elif (data[0] == "Private" and data[-1] == "<50K"):
            private_negative += 1
        elif (data[0] == "Self-emp" and data[-1] == "<50K"):
            self_emp_negative += 1
    Fwork.add_values([['Not Working', '<50K', not_working_negative/total], ['Not Working', '>=50K', 1 - not_working_negative/total], 
                        ['Government', '<50K', government_negative/total], ['Government', '>=50K', 1 - government_negative/total],
                        ['Private', '<50K', private_negative/total], ['Private', '>=50K', 1 - private_negative/total],
                        ['Self-emp', '<50K', self_emp_negative/total], ['Self-emp', '>=50K', 1 - self_emp_negative/total]])
    # education
    less_than_12_negative = 0
    hs_graduate_negative = 0
    associate_negative = 0
    professional_negative = 0
    bachelors_negative = 0
    masters_negative = 0
    doctorate_negative = 0
    for data in input_data:
        if (data[1] == "<Gr12" and data[-1] == "<50K"):
            less_than_12_negative += 1
        elif (data[1] == "HS-Graduate" and data[-1] == "<50K"):
            hs_graduate_negative += 1
        elif (data[1] == "Associate" and data[-1] == "<50K"):
            associate_negative += 1
        elif (data[1] == "Professional" and data[-1] == "<50K"):
            professional_negative += 1
        elif (data[1] == "Bachelors" and data[-1] == "<50K"):
            bachelors_negative += 1
        elif (data[1] == "Masters" and data[-1] == "<50K"):
            masters_negative += 1
        elif (data[1] == "Doctorate" and data[-1] == "<50K"):
            doctorate_negative += 1
    Fedu.add_values([['<Gr12', '<50K', less_than_12_negative/total], ['<Gr12', '>=50K', 1 - less_than_12_negative/total],
                        ['HS-Graduate', '<50K', hs_graduate_negative/total], ['HS-Graduate', '>=50K', 1 - hs_graduate_negative/total],
                        ['Associate', '<50K', associate_negative/total], ['Associate', '>=50K', 1 - associate_negative/total],
                        ['Professional', '<50K', professional_negative/total], ['Professional', '>=50K', 1 - professional_negative/total],
                        ['Bachelors', '<50K', bachelors_negative/total], ['Bachelors', '>=50K', 1 - bachelors_negative/total],
                        ['Masters', '<50K', masters_negative/total], ['Masters', '>=50K', 1 - masters_negative/total],
                        ['Doctorate', '<50K', doctorate_negative/total], ['Doctorate', '>=50K', 1 - doctorate_negative/total]])
    # occupation
    adm_clerical_negative = 0
    military_negative = 0
    manual_negative = 0
    office_negative = 0
    service_negative = 0
    professional_negative = 0
    for data in input_data:
        if (data[3] == "Admin" and data[-1] == "<50K"):
            adm_clerical_negative += 1
        elif (data[3] == "Military" and data[-1] == "<50K"):
            military_negative += 1
        elif (data[3] == "Manual Labour" and data[-1] == "<50K"):
            manual_negative += 1
        elif (data[3] == "Office Labour" and data[-1] == "<50K"):
            office_negative += 1
        elif (data[3] == "Service" and data[-1] == "<50K"):
            service_negative += 1
        elif (data[3] == "Professional" and data[-1] == "<50K"):
            professional_negative += 1
    Focc.add_values([['Admin', '<50K', adm_clerical_negative/total], ['Admin', '>=50K', 1 - adm_clerical_negative/total],
                        ['Military', '<50K', military_negative/total], ['Military', '>=50K', 1 - military_negative/total],
                        ['Manual Labour', '<50K', manual_negative/total], ['Manual Labour', '>=50K', 1 - manual_negative/total],
                        ['Office Labour', '<50K', office_negative/total], ['Office Labour', '>=50K', 1 - office_negative/total],
                        ['Service', '<50K', service_negative/total], ['Service', '>=50K', 1 - service_negative/total],
                        ['Professional', '<50K', professional_negative/total], ['Professional', '>=50K', 1 - professional_negative/total]])
    # relationship
    wife_negative = 0
    own_child_negative = 0
    husband_negative = 0
    not_in_family_negative = 0
    other_relative_negative = 0
    unmarried_negative = 0
    for data in input_data:
        if (data[4] == "Wife" and data[-1] == "<50K"):
            wife_negative += 1
        elif (data[4] == "Own-child" and data[-1] == "<50K"):
            own_child_negative += 1
        elif (data[4] == "Husband" and data[-1] == "<50K"):
            husband_negative += 1
        elif (data[4] == "Not-in-family" and data[-1] == "<50K"):
            not_in_family_negative += 1
        elif (data[4] == "Other-relative" and data[-1] == "<50K"):
            other_relative_negative += 1
        elif (data[4] == "Unmarried" and data[-1] == "<50K"):
            unmarried_negative += 1
    Frel.add_values([['Wife', '<50K', wife_negative/total], ['Wife', '>=50K', 1 - wife_negative/total],
                        ['Own-child', '<50K', own_child_negative/total], ['Own-child', '>=50K', 1 - own_child_negative/total],
                        ['Husband', '<50K', husband_negative/total], ['Husband', '>=50K', 1 - husband_negative/total],
                        ['Not-in-family', '<50K', not_in_family_negative/total], ['Not-in-family', '>=50K', 1 - not_in_family_negative/total],
                        ['Other-relative', '<50K', other_relative_negative/total], ['Other-relative', '>=50K', 1 - other_relative_negative/total],
                        ['Unmarried', '<50K', unmarried_negative/total], ['Unmarried', '>=50K', 1 - unmarried_negative/total]])
    # race
    white_negative = 0
    black_negative = 0
    asian_pac_islander_negative = 0
    amer_indian_eskimo_negative = 0
    other_negative = 0
    for data in input_data:
        if (data[5] == "White" and data[-1] == "<50K"):
            white_negative += 1
        elif (data[5] == "Black" and data[-1] == "<50K"):
            black_negative += 1
        elif (data[5] == "Asian-Pac-Islander" and data[-1] == "<50K"):
            asian_pac_islander_negative += 1
        elif (data[5] == "Amer-Indian-Eskimo" and data[-1] == "<50K"):
            amer_indian_eskimo_negative += 1
        elif (data[5] == "Other" and data[-1] == "<50K"):
            other_negative += 1
    Frac.add_values([['White', '<50K', white_negative/total], ['White', '>=50K', 1 - white_negative/total],
                        ['Black', '<50K', black_negative/total], ['Black', '>=50K', 1 - black_negative/total],
                        ['Asian-Pac-Islander', '<50K', asian_pac_islander_negative/total], ['Asian-Pac-Islander', '>=50K', 1 - asian_pac_islander_negative/total],
                        ['Amer-Indian-Eskimo', '<50K', amer_indian_eskimo_negative/total], ['Amer-Indian-Eskimo', '>=50K', 1 - amer_indian_eskimo_negative/total],
                        ['Other', '<50K', other_negative/total], ['Other', '>=50K', 1 - other_negative/total]])
    # gender
    male_negative = 0
    female_negative = 0
    for data in input_data:
        if (data[6] == "Male" and data[-1] == "<50K"):
            male_negative += 1
        elif (data[6] == "Female" and data[-1] == "<50K"):
            female_negative += 1
    Fgen.add_values([['Male', '<50K', male_negative/total], ['Male', '>=50K', 1 - male_negative/total],
                    ['Female', '<50K', female_negative/total], ['Female', '>=50K', 1 - female_negative/total]])
    # country
    north_america_negative = 0
    south_america_negative = 0
    europe_negative = 0
    asia_negative = 0
    middle_east_negative = 0
    carribean_negative = 0
    for data in input_data:
        if (data[7] == "North-America" and data[-1] == "<50K"):
            north_america_negative += 1
        elif (data[7] == "South-America" and data[-1] == "<50K"):
            south_america_negative += 1
        elif (data[7] == "Europe" and data[-1] == "<50K"):
            europe_negative += 1
        elif (data[7] == "Asia" and data[-1] == "<50K"):
            asia_negative += 1
        elif (data[7] == "Middle-East" and data[-1] == "<50K"):
            middle_east_negative += 1
        elif (data[7] == "Carribean" and data[-1] == "<50K"):
            carribean_negative += 1
    Fcou.add_values([['North-America', '<50K', north_america_negative/total], ['North-America', '>=50K', 1 - north_america_negative/total],
                        ['South-America', '<50K', south_america_negative/total], ['South-America', '>=50K', 1 - south_america_negative/total],
                        ['Europe', '<50K', europe_negative/total], ['Europe', '>=50K', 1 - europe_negative/total],
                        ['Asia', '<50K', asia_negative/total], ['Asia', '>=50K', 1 - asia_negative/total],
                        ['Middle-East', '<50K', middle_east_negative/total], ['Middle-East', '>=50K', 1 - middle_east_negative/total],
                        ['Carribean', '<50K', carribean_negative/total], ['Carribean', '>=50K', 1 - carribean_negative/total]])
    # marital status
    # marital_status = Variable("MaritalStatus", ['Not-Married', 'Married', 'Separated', 'Widowed'])
    # marital status
    not_married_negative = 0
    married_negative = 0
    separated_negative = 0
    widowed_negative = 0
    for data in input_data:
        if (data[2] == "Not-Married" and data[-1] == "<50K"):
            not_married_negative += 1
        elif (data[2] == "Married" and data[-1] == "<50K"):
            married_negative += 1
        elif (data[2] == "Separated" and data[-1] == "<50K"):
            separated_negative += 1
        elif (data[2] == "Widowed" and data[-1] == "<50K"):
            widowed_negative += 1
    Fmar.add_values([['Not-Married', '<50K', not_married_negative/total], ['Not-Married', '>=50K', 1 - not_married_negative/total],
                        ['Married', '<50K', married_negative/total], ['Married', '>=50K', 1 - married_negative/total],
                        ['Separated', '<50K', separated_negative/total], ['Separated', '>=50K', 1 - separated_negative/total],
                        ['Widowed', '<50K', widowed_negative/total], ['Widowed', '>=50K', 1 - widowed_negative/total]])

    # 5. define BN
    bn = BN(name, variables, factors)
    # for f in bn.Factors:
    #     f.print_table()
    return bn


def Explore(Net, question):
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
    ### YOUR CODE HERE ###
    print("start")
    res = []
    odd = [1, 3, 5]
    if question in odd:
        gender = "Female"
    else:
        gender = "Male"
    if question == 3:
        for f in Net.Factors:
            print(f.name)
            if f.name == "P(Salary|Gender)":
                return f.get_value(['Female', '>=50K'])
    if question == 4:
        for f in Net.Factors:
            if f.name == "P(Salary|Gender)":
                return f.get_value(['Male', '>=50K'])
    #1. Create a core evidence set (E1) using the values assigned to the following variables: [Work, Occupation, Education, and Relationship Status]
    evidence = ["Work", "Occupation", "Education", "Relationship"]
    qvar = None
    for var in Net.Variables:
        if var.name == "Work":
            var.set_evidence("Private")
        elif var.name == "Occupation":
            var.set_evidence("Professional")
        elif var.name == "Education":
            var.set_evidence("Bachelors")
        elif var.name == "Relationship":
            var.set_evidence("Wife")
        elif var.name == "Salary":
            qvar = var
        elif var.name == "Gender":
            var.set_evidence(gender)
    res.append(VE(Net, qvar, evidence))
    #2. Create an extended evidence set (E2) using the values assigned to the following variables: [Work, Occupation, Education, Relationship Status, and Gender] 
    for var in Net.Variables:
        if var.name == "Work":
            var.set_evidence("Private")
        elif var.name == "Occupation":
            var.set_evidence("Professional")
        elif var.name == "Education":
            var.set_evidence("Bachelors")
        elif var.name == "Relationship":
            var.set_evidence("Wife")
        elif var.name == "Gender":
            var.set_evidence("Female")
        elif var.name == "Salary":
            qvar = var
        elif var.name == "Gender":
            var.set_evidence(gender)
    res.append(VE(Net, qvar, evidence))
    #3. Use the two evidence sets to predict Salary (S) for the data in the test set using your Naive Bayes model.
    # print(abs(res[0][1] - res[1][1]))
    if question == 1 or question == 2:
        return abs(res[0][1] - res[1][1])
    elif question == 5 or question == 6:
        if res[0][1] > 0.5:
            return res[0][1]
        else:
            return 0
            
    

