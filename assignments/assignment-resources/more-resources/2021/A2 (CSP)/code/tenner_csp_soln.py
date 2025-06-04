#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete the warehouse domain.  

'''
Construct and return Tenner Grid CSP models.
'''

from cspbase import *
import itertools

def tenner_csp_model_1(initial_tenner_board):
    '''Return a CSP object representing a Tenner Grid CSP problem along 
       with an array of variables for the problem. That is return

       tenner_csp, variable_array

       where tenner_csp is a csp representing tenner grid using model_1
       and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

       such that variable_array[i][j] is the Variable (object) that
       you built to represent the value to be placed in cell i,j of
       the Tenner Grid (only including the first n rows, indexed from 
       (0,0) to (n,9)) where n can be 3 to 7.
       
       
       The input board is specified as a pair (n_grid, last_row). 
       The first element in the pair is a list of n length-10 lists.
       Each of the n lists represents a row of the grid. 
       If a -1 is in the list it represents an empty cell. 
       Otherwise if a number between 0--9 is in the list then this represents a 
       pre-set board position. E.g., the board
    
       ---------------------  
       |6| |1|5|7| | | |3| |
       | |9|7| | |2|1| | | |
       | | | | | |0| | | |1|
       | |9| |0|7| |3|5|4| |
       |6| | |5| |0| | | | |
       ---------------------
       would be represented by the list of lists
       
       [[6, -1, 1, 5, 7, -1, -1, -1, 3, -1],
        [-1, 9, 7, -1, -1, 2, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, 0, -1, -1, -1, 1],
        [-1, 9, -1, 0, 7, -1, 3, 5, 4, -1],
        [6, -1, -1, 5, -1, 0, -1, -1, -1,-1]]
       
       
       This routine returns model_1 which consists of a variable for
       each cell of the board, with domain equal to {0-9} if the board
       has a 0 at that position, and domain equal {i} if the board has
       a fixed number i at that cell.
       
       model_1 contains BINARY CONSTRAINTS OF NOT-EQUAL between
       all relevant variables (e.g., all pairs of variables in the
       same row, etc.).
       model_1 also constains n-nary constraints of sum constraints for each 
       column.
    '''

   #first define the variables
    i = 0
    var_array = []
    for row_list in initial_tenner_board[0]:
        var_array.append([])
        j = 0
        for col in row_list:
            cell = initial_tenner_board[0][i][j]
            var = Variable("V{},{}".format(i+1, j+1))
            var_array[i].append(var)
            #Set domain values
            if cell == -1:
                var.add_domain_values([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            else:
                var.add_domain_values([cell])
            
            j = j+1
        i = i + 1


    #Set up the constraints

    constraint_list = []

    #Binary Row constraints
    for row in var_array:
        constraint_list.extend(binary_not_equal(row))
    #Binary contiguous cell constraints
    constraint_list.extend(contiguous_not_equal(var_array))
    #Sum constraints
    for j in range(len(var_array[0])):
        colj = [row[j] for row in var_array]
        con_name = "SUM{}".format(j+1)
        constraint_list.extend(sum_constraints(colj, initial_tenner_board[1][j], con_name))

     #Now create csp object
    vars = []
    for row in var_array:
        for v in row:
            vars.append(v)
            
    csp = CSP("Tenner-M1", vars)
    for con in constraint_list:
        csp.add_constraint(con)
    return csp, var_array
##############################

def binary_not_equal(var_list):
    '''Post a not equal constraint between all pairs of variables in var_list
       return list of constructed constraint objects''' 
 
    constraints = []
    for i in range(len(var_list)):
        for j in range(i+1,len(var_list)):
            c = Constraint("NE({},{})".format(var_list[i].name, var_list[j].name),
                           [var_list[i], var_list[j]])
            
            i_vals = var_list[i].domain()
            j_vals = var_list[j].domain()

            sat_tuples = []

            for i_val in i_vals:
                for j_val in j_vals:
                    if j_val != i_val:
                        sat_tuples.append((i_val,j_val))
            c.add_satisfying_tuples(sat_tuples)
            constraints.append(c)
            #print(c)
            #print(sat_tuples)

    #print("{}".format(constraints))
    return constraints

def contiguous_not_equal(var_array):
    '''Post a not equal constraint between all contiguous cells in the grid
       return list of constructed constraint objects''' 
 
    #
    constraints = []
    rows = len(var_array)
    cols = 0
    if rows > 0:
        cols = len(var_array[0])
    for i in range(rows - 1):
        for j in range(cols):
            #Compare against cell below
            constraints.append(neq_constraint_given_indices(var_array, i, j, i+1, j))
            #Compare against cell below and left
            if j > 0:
                constraints.append(neq_constraint_given_indices(var_array, i, j, i+1, j-1))
            #Compare against cell below and right, and cell right
            if j < (cols - 1):
                constraints.append(neq_constraint_given_indices(var_array, i, j, i+1, j+1))
                #The following could be omitted, as this constraint is
                #added by the row constraints
                constraints.append(neq_constraint_given_indices(var_array, i, j, i, j+1))

    return constraints

def neq_constraint_given_indices(var_array, i, j, x, y):
    '''Add a not equal constraint between variable at index i j
       and variable at index x y
       return list of constructed constraint objects'''

    c = Constraint("NE({},{})".format(var_array[i][j].name, var_array[x][y].name),
                           [var_array[i][j], var_array[x][y]])
            
    i_vals = var_array[i][j].domain()
    x_vals = var_array[x][y].domain()

    sat_tuples = []

    for i_val in i_vals:
        for x_val in x_vals:
            if x_val != i_val:
                sat_tuples.append((i_val,x_val))
    c.add_satisfying_tuples(sat_tuples)
    return c

def sum_constraints(col, total, name):
    '''Add a sum constraint for the specified column
    Return the constraint'''

    c = Constraint(name, col)
    sat_tuples = []
    domains = [(cell.domain()) for cell in col]
    permutations = itertools.product(*domains)
    for val in permutations:
        if total == sum(val):
            sat_tuples.append(val)
    c.add_satisfying_tuples(sat_tuples)
    return [c]
    


def tenner_csp_model_2(initial_tenner_board):
    '''Return a CSP object representing a Tenner Grid CSP problem along 
       with an array of variables for the problem. That is return

       tenner_csp, variable_array

       where tenner_csp is a csp representing tenner using model_1
       and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

       such that variable_array[i][j] is the Variable (object) that
       you built to represent the value to be placed in cell i,j of
       the Tenner Grid (only including the first n rows, indexed from 
       (0,0) to (n,9)) where n can be 3 to 7.

       The input board takes the same input format (a list of n length-10 lists
       specifying the board as tenner_csp_model_1.
    
       The variables of model_2 are the same as for model_1: a variable
       for each cell of the board, with domain equal to {0-9} if the
       board has a -1 at that position, and domain equal {i} if the board
       has a fixed number i at that cell.

       However, model_2 has different constraints. In particular, instead
       of binary non-equals constaints model_2 has a combination of n-nary 
       all-different constraints: all-different constraints for the variables in
       each row, contiguous cells (including diagonally contiguous cells), and 
       sum constraints for each column. Each of these constraints is over more 
       than two variables (some of these variables will have
       a single value in their domain). model_2 should create these
       all-different constraints between the relevant variables.
    '''

#first define the variables
    i = 0
    var_array = []
    for row_list in initial_tenner_board[0]:
        var_array.append([])
        j = 0
        for col in row_list:
            cell = initial_tenner_board[0][i][j]
            var = Variable("V{},{}".format(i+1, j+1))
            var_array[i].append(var)
            #Set domain values
            if cell == -1:
                var.add_domain_values([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            else:
                var.add_domain_values([cell])
            
            j = j+1
        i = i + 1


    #Set up the constraints

    constraint_list = []

    #Binary Row constraints
    row_ind = 0
    for row in var_array:
        con_name = "ALL_DIF{}".format(row_ind+1)
        constraint_list.extend(nary_all_different_constraints(row, con_name))
        row_ind = row_ind + 1
    #Binary contiguous cell constraints
    constraint_list.extend(contiguous_not_equal(var_array))
    #Sum constraints
    for j in range(len(var_array[0])):
        colj = [row[j] for row in var_array]
        con_name = "SUM{}".format(j+1)
        constraint_list.extend(sum_constraints(colj, initial_tenner_board[1][j], con_name))

     #Now create csp object
    vars = []
    for row in var_array:
        for v in row:
            vars.append(v)
            
    csp = CSP("Tenner-M1", vars)
    for con in constraint_list:
        csp.add_constraint(con)
    return csp, var_array


def nary_all_different_constraints(row, name):
    '''Add all-different constraints for the given row
    Return the constraint'''

    c = Constraint(name, row)
    sat_tuples = []
    domains = [(cell.domain()) for cell in row]
    permutations = itertools.product(*domains)
    for val in permutations:
        #Ensure all values are different
        if len(set(val)) == len(val):
            sat_tuples.append(val)
    c.add_satisfying_tuples(sat_tuples)
    return [c]