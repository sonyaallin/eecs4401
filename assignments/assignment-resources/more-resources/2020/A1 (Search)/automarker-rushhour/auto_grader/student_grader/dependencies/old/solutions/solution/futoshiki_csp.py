#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented.

'''
Construct and return Futoshiki CSP models.
'''

from dependencies.cspbase import *
import itertools

def futoshiki_csp_model_1(initial_futoshiki_board):
    '''Return a CSP object representing a Futoshiki CSP problem along with an
    array of variables for the problem. That is return

    futoshiki_csp, variable_array

    where futoshiki_csp is a csp representing futoshiki using model_1 and
    variable_array is a list of lists

    [ [  ]
      [  ]
      .
      .
      .
      [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to
    represent the value to be placed in cell i,j of the futoshiki board
    (indexed from (0,0) to (n-1,n-1))


    The input board is specified as a list of n lists. Each of the n lists
    represents a row of the board. If a 0 is in the list it represents an empty
    cell. Otherwise if a number between 1--n is in the list then this
    represents a pre-set board position.

    Each list is of length 2n-1, with each space on the board being separated
    by the potential inequality constraints. '>' denotes that the previous
    space must be bigger than the next space; '<' denotes that the previous
    space must be smaller than the next; '.' denotes that there is no
    inequality constraint.

    E.g., the board

    -------------------
    | > |2| |9| | |6| |
    | |4| | | |1| | |8|
    | |7| <4|2| | | |3|
    |5| | | | | |3| | |
    | | |1| |6| |5| | |
    | | <3| | | | | |6|
    |1| | | |5|7| |4| |
    |6> | |9| < | |2| |
    | |2| | |8| <1| | |
    -------------------
    would be represented by the list of lists

    [[0,>,0,.,2,.,0,.,9,.,0,.,0,.,6,.,0],
     [0,.,4,.,0,.,0,.,0,.,1,.,0,.,0,.,8],
     [0,.,7,.,0,<,4,.,2,.,0,.,0,.,0,.,3],
     [5,.,0,.,0,.,0,.,0,.,0,.,3,.,0,.,0],
     [0,.,0,.,1,.,0,.,6,.,0,.,5,.,0,.,0],
     [0,.,0,<,3,.,0,.,0,.,0,.,0,.,0,.,6],
     [1,.,0,.,0,.,0,.,5,.,7,.,0,.,4,.,0],
     [6,>,0,.,0,.,9,.,0,<,0,.,0,.,2,.,0],
     [0,.,2,.,0,.,0,.,8,.,0,<,1,.,0,.,0]


    This routine returns Model_1 which consists of a variable for each cell of
    the board, with domain equal to [1,...,n] if the board has a 0 at that
    position, and domain equal [i] if the board has a fixed number i at that
    cell.

    Model_1 also contains BINARY CONSTRAINTS OF NOT-EQUAL between all relevant
    variables (e.g., all pairs of variables in the same row, etc.).

    All of the constraints of Model_1 MUST BE binary constraints (i.e.,
    constraints whose scope includes two and only two variables).
    '''

    ##first process the input so that we have a board, and a set of inequality constraints
    
    inequality_rows, cell_rows = process_board(initial_futoshiki_board)
    max_val = len(initial_futoshiki_board)

    ##now define the variables & add their domain values
    var_array = make_var_array(cell_rows,max_val)


    ##Set up the constraints
    constraint_list = []

    ##row constraints
    for row in var_array:
        constraint_list.extend(post_all_pairs(row))

    #col constraints
    for j in range(len(var_array[0])):
        colj = [row[j] for row in var_array]
        constraint_list.extend(post_all_pairs(colj))

    #inequality constraints
    constraint_list.extend(make_ineq_constraints(var_array,inequality_rows))

    ##create csp object
    vars = []
    for row in var_array:
        for v in row:
            vars.append(v)
            
    csp = CSP("Futoshiki-M1", vars)
    for con in constraint_list:
        csp.add_constraint(con)
    return csp, var_array


##############################

def futoshiki_csp_model_2(initial_futoshiki_board):
    '''Return a CSP object representing a futoshiki CSP problem along with an
    array of variables for the problem. That is return

    futoshiki_csp, variable_array

    where futoshiki_csp is a csp representing futoshiki using model_2 and
    variable_array is a list of lists

    [ [  ]
      [  ]
      .
      .
      .
      [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to
    represent the value to be placed in cell i,j of the futoshiki board
    (indexed from (0,0) to (n-1,n-1))

    The input board takes the same input format (a list of n lists of size 2n-1
    specifying the board) as futoshiki_csp_model_1.

    The variables of Model_2 are the same as for Model_1: a variable for each
    cell of the board, with domain equal to [1,...,n] if the board has a 0 at
    that position, and domain equal [n] if the board has a fixed number i at
    that cell.

    However, Model_2 has different constraints. In particular, instead of
    binary non-equals constaints Model_2 has 2*n all-different constraints:
    all-different constraints for the variables in each of the n rows, and n
    columns. Each of these constraints is over n-variables (some of these
    variables will have a single value in their domain). Model_2 should create
    these all-different constraints between the relevant variables, and then
    separately generate the appropriate binary inequality constraints as
    required by the board. There should be j of these constraints, where j is
    the number of inequality symbols found on the board.  
    '''

    ##first process the input so that we have a board, and a set of inequality constraints
    inequality_rows, cell_rows = process_board(initial_futoshiki_board)
    max_val = len(initial_futoshiki_board)

    ##now define the variables & add their domain values
    var_array = make_var_array(cell_rows,max_val)

    
    ##Set up the constraints
    constraint_list = []

    ##init row constraints
    for row in var_array:
        constraint_list.append(Constraint("Row{}".format(var_array.index(row)), list(row)))

    #init col constraints
    for j in range(len(var_array[0])):
        colj = [row[j] for row in var_array]
        constraint_list.append(Constraint("Col{}".format(j),colj))

    #generate sat tuples for row & col
    for c in constraint_list:
        tmp_tuples = [] 
        sat_tuples = [[]]
        for var in c.scope:
            for val in var.domain():
                for t in sat_tuples:
                    if not val in t:
                        tnew = list(t)
                        tnew.append(val)
                        tmp_tuples.append(tnew)
            sat_tuples = tmp_tuples
            tmp_tuples = []
        c.add_satisfying_tuples(sat_tuples)
                    
    #add inequality constraints
    constraint_list.extend(make_ineq_constraints(var_array,inequality_rows))

    #Now create csp object
    vars = []
    for row in var_array:
        for v in row:
            vars.append(v)
            
    csp = CSP("Futoshiki-M2", vars)
    for con in constraint_list:
        csp.add_constraint(con)
    return csp, var_array

def make_var_array(cell_rows,max_val):
    var_array = [] 
    i = 0
    for row in cell_rows:
        var_array.append([])
        j = 0
        for cell in row:
            var = Variable("V{},{}".format(i,j))    
            var_array[i].append(var)
            if cell == 0:
                var.add_domain_values(list(range(1,max_val+1)))
            else:
                var.add_domain_values([cell])
            j+=1
        i+=1
    return var_array

def process_board(initial_futoshiki_board):

    inequality_rows = []
    cell_rows = [] 

    for row in initial_futoshiki_board:
        indx = 0
        ineq_row = [] 
        c_row = [] 
        while indx < len(row):
            c_row.append(int(row[indx]))
            if indx+1 < len(row):
                ineq_row.append(row[indx+1].strip())
            indx = indx + 2
        inequality_rows.append(ineq_row)
        cell_rows.append(c_row)
    return inequality_rows,cell_rows

def post_all_pairs(var_list):
    '''Post a not equal constraint between all pairs of variables in var_list
       return list of constructed constraint objects''' 
 
    constraints = []
    for i in range(len(var_list)):
        for j in range(i+1,len(var_list)):
            c = Constraint("NE({},{})".format(var_list[i].name, var_list[j].name),
                           [var_list[i], var_list[j]])
            sat_tuples = []
            for t in itertools.product(var_list[i].domain(), var_list[j].domain()):
                if t[0] != t[1]:
                    sat_tuples.append(t)
            c.add_satisfying_tuples(sat_tuples)
            constraints.append(c)
    return constraints

def make_ineq_constraints(var_array,inequality_rows):
    ineq_constraints = [] 
    i = 0
    for row in inequality_rows:
        j = 0 
        for comp in row:
            if comp == '.':
                pass
            else:
                if comp == '>':
                    var1 = var_array[i][j]
                    var2 = var_array[i][j+1]
                    c = Constraint(">({},{})".format(var1.name,var2.name),[var1,var2])
                    sat_tuples = [] 
                    for t in itertools.product(var1.domain(), var2.domain()):
                        if t[0] > t[1]:
                            sat_tuples.append(t)
                    c.add_satisfying_tuples(sat_tuples)
                    ineq_constraints.append(c)
                    
                elif comp == '<':
                    var1 = var_array[i][j]
                    var2 = var_array[i][j+1]
                    c = Constraint("<({},{})".format(var1.name,var2.name),[var1,var2])
                    sat_tuples = [] 
                    for t in itertools.product(var1.domain(), var2.domain()):
                        if t[0] < t[1]:
                            sat_tuples.append(t)
                    c.add_satisfying_tuples(sat_tuples)
                    ineq_constraints.append(c)
                    

                else:
                    assert False, "Formatting error: %r" % comp
            j+=1 
        i+=1
    return ineq_constraints



