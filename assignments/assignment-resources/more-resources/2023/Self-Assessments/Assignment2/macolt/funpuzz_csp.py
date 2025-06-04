#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *

def makeVariables(varList, size):
    """Used to make a 2d array of all variables for a board of size 'size'
    Takes input a list to be filled, and the size of the board"""
    domain = []
    for i in range(size):
        domain.append(i+1)
    for i in range(size):
        for j in range(size):
            varList[i][j] = Variable((str(i+1)+str(j+1)),domain)
                    

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
    size = funpuzz_grid[0][0]
    variable_array = [[None for j in range(size)] for i in range(size)]
    #Call helper to make variable array
    makeVariables(variable_array,size)
    varList = []
    #compress variable array to 1d for making csp
    for vl in variable_array:
        for v in vl:
            varList.append(v)
    funpuzz_csp = CSP("binary-ne", varList)
    tupleList = []
    #Making all possible combinations of satisfying tuples for binary not equal given board size
    for a in range(size):
        for b in range(size):
            if (a != b):
                tupleList.append((a+1,b+1))
    #iterating over width
    for i in range(size):
        #iterating over height
        for j in range(size):
            #for variables in the same row
            for x in range(i+1,size):
                constraint = Constraint((str(i+1)+str(j+1) + "=/=" + str(x+1)+str(j+1)), [variable_array[i][j],variable_array[x][j]])
                constraint.add_satisfying_tuples(tupleList)
                funpuzz_csp.add_constraint(constraint)
            #for variables in the same column
            for y in range(j+1,size):
                constraint = Constraint((str(i+1)+str(j+1) + "=/=" + str(i+1)+str(y+1)), [variable_array[i][j],variable_array[i][y]])
                constraint.add_satisfying_tuples(tupleList)
                funpuzz_csp.add_constraint(constraint)
    return funpuzz_csp, variable_array


def nary_tuple(rList, curr, ret):
    """takes in a list of elements rList, and will append to ret
    all possible permuations of items in rList. This is used to
    get all tuples to satisfy a row, n-ary all different
    constraint"""
    if (len(rList) == 1):
        ret.append(curr+(rList[0],))
        return
    for i in rList:
        listtemp = rList.copy()
        listtemp.remove(i)
        currtemp = curr
        currtemp = currtemp + (i,)
        nary_tuple(listtemp, currtemp, ret)
        
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
    size = funpuzz_grid[0][0]
    variable_array = [[None for j in range(size)] for i in range(size)]
    #Call helper to make variable array
    makeVariables(variable_array,size)
    varList = []
    #compress variable array to 1d for making csp
    for vl in variable_array:
        for v in vl:
            varList.append(v)
    funpuzz_csp = CSP("nary", varList)
    inc = []
    #making list for generating constraint tuples
    for i in range(size):
        inc.append(i+1)
    tupleList = []
    #generating constraint tuples
    nary_tuple(inc, (), tupleList)
    #iterating over side length
    for i in range(size):
        rowVar = []
        colVar = []
        #populating variable lists for each row/column
        for j in range(size):
            rowVar.append(variable_array[i][j])
            colVar.append(variable_array[j][i])
        constraint = Constraint("Row " + str(i+1), rowVar)
        constraint.add_satisfying_tuples(tupleList)
        funpuzz_csp.add_constraint(constraint)
        constraint = Constraint("Col " + str(i+1), colVar)
        constraint.add_satisfying_tuples(tupleList)
        funpuzz_csp.add_constraint(constraint)
    return funpuzz_csp, variable_array


def permute(t, cur, satTup):
    """Takes a tuple t and permutes the values. Appends the value to
    satTup. This is used for "-" and "/" since the make constraints
    function only adds satisfying constratints in the order the
    variables are set in the constraint"""
    if len(t) == 0:
        satTup.append(tuple(cur))
        return 
    tl = list(t)
    for i in tl:
        tempcur = cur.copy()
        tempcur.append(i)
        temptl = tl.copy()
        temptl.remove(i)
        permute(temptl, tempcur, satTup)
        

def genConst(left,size,satTup,op,sol):
    """Generates tuples for constraints recursivly. Left
    is number of variables and op is the operation. These
    values will be appended to satTup"""
    for i in range(1,size + 1):
        if (op == 0):
            genConst0(i,(i,),left-1,size,satTup,sol)
        if (op == 1):
            genConst1(i,(i,),left-1,size,satTup,sol)
        if (op == 2):
            genConst2(i,(i,),left-1,size,satTup,sol)
        if (op == 3):
            genConst3(i,(i,),left-1,size,satTup,sol)
    if (op == 1 or op == 2):
        tempSatTup = []
        for i in satTup:
            permute(i, [], tempSatTup)
        for i in tempSatTup:
            if i not in satTup:
                satTup.append(i)

def genConst0(curVal,curTup,left,size,satTup,sol):
    """Helper of genConst for addition operation"""
    if left == 0:
        if curVal == sol:
            satTup.append(curTup)
        return
    for i in range(1,size + 1):
        tempTup = curTup+(i,)
        genConst0(curVal+i,tempTup,left-1,size,satTup,sol)
        
        
def genConst1(curVal,curTup,left,size,satTup,sol):
    """Helper of genConst for subtraction operation"""
    if left == 0:
        if curVal == sol:
            satTup.append(curTup)
        return
    for i in range(1,size + 1):
        tempTup = curTup+(i,)
        genConst1(curVal-i,tempTup,left-1,size,satTup,sol)

def genConst2(curVal,curTup,left,size,satTup,sol):
    """Helper of genConst for division operation"""    
    if left == 0:
        if curVal == sol:
            satTup.append(curTup)
        return
    for i in range(1,size + 1):
        tempTup = curTup+(i,)
        genConst2(curVal//i,tempTup,left-1,size,satTup,sol)

def genConst3(curVal,curTup,left,size,satTup,sol):
    """Helper of genConst for multiplication operation"""
    if left == 0:
        if curVal == sol:
            satTup.append(curTup)
        return
    for i in range(1,size + 1):
        tempTup = curTup+(i,)
        genConst3(curVal*i,tempTup,left-1,size,satTup,sol)

        


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
    #generates base csp and variable array from binary ne. I find it performs better
    funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)
    size = funpuzz_grid[0][0]
    #iterating over cages
    for i in funpuzz_grid:
        #ensuring not size element
        if len(i) != 1:
            tupleList = []
            genConst(len(i)-2,size,tupleList,i[-1],i[-2])
            varlist = []
            #iterating over variables of cage
            for j in range(len(i)-2):
                varlist.append(variable_array[(i[j]//10)-1][(i[j]%10)-1])
            constraint = Constraint("cage-constraint:" + str(i), varlist)
            constraint.add_satisfying_tuples(tupleList)
            funpuzz_csp.add_constraint(constraint)
    return funpuzz_csp, variable_array


