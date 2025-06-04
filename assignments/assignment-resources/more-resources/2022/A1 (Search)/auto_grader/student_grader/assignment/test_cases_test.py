from test_tools import max_grade

@max_grade(1)
def addOne(student_mod):
    res = student_mod.addOne(1)
    if res == 2:
        return 1, "test_case description success"
    return 0, "tc description fail: BOBOBBOBOOOOOOOOO"
