from assignment import A2_test_cases_aux
from utils.test_tools import max_grade

PROPAGATORS = "propagators.py"
MODELS = "futoshiki_csp.py"

@max_grade(1)
def test_simple_FC(modules):
    return A2_test_cases_aux.test_simple_FC(modules[PROPAGATORS])

@max_grade(1)
def test_simple_GAC(modules):
    return A2_test_cases_aux.test_simple_GAC(modules[PROPAGATORS])

@max_grade(1)
def test_three_queen_FC(modules):
    return A2_test_cases_aux.three_queen_FC(modules[PROPAGATORS])

@max_grade(1)
def test_three_queen_GAC(modules):
    return A2_test_cases_aux.three_queen_GAC(modules[PROPAGATORS])

# @max_grade(1)
# def test_fc_1(modules):
#     return A2_test_cases_aux.test_1(modules[PROPAGATORS].prop_FC, "FC")

# @max_grade(1)
# def test_gac_1(modules):
#     return A2_test_cases_aux.test_1(modules[PROPAGATORS].prop_GAC, "GAC")

# @max_grade(1)
# def test_fc_2(modules):
#     return A2_test_cases_aux.test_2(modules[PROPAGATORS].prop_FC, "FC")

# @max_grade(1)
# def test_gac_2(modules):
#     return A2_test_cases_aux.test_2(modules[PROPAGATORS].prop_GAC, "GAC")

# @max_grade(1)
# def test_fc_3(modules):
#     return A2_test_cases_aux.test_3(modules[PROPAGATORS].prop_FC, "FC")

# @max_grade(1)
# def test_gac_3(modules):
#     return A2_test_cases_aux.test_3(modules[PROPAGATORS].prop_GAC, "GAC")

# @max_grade(5)
# def test_tiny_adder_fc(modules):
#     return A2_test_cases_aux.test_tiny_adder_FC(modules[PROPAGATORS])

# @max_grade(5)
# def test_tiny_adder_gac(modules):
#     return A2_test_cases_aux.test_tiny_adder_GAC(modules[PROPAGATORS])

# @max_grade(3)
# def test_no_pruning_1_fc(modules):
#     return A2_test_cases_aux.test_no_pruning_FC(modules[PROPAGATORS])

# @max_grade(3)
# def test_no_pruning_2_fc(modules):
#     return A2_test_cases_aux.test_no_pruning2_FC(modules[PROPAGATORS])

# @max_grade(6)
# def test_no_pruning_gac(modules):
#     return A2_test_cases_aux.test_no_pruning_GAC(modules[PROPAGATORS])

# @max_grade(4)
# def test_10queens_gac(modules):
#     return A2_test_cases_aux.test_gac_10queens(modules[PROPAGATORS])

# @max_grade(4)
# def test_10queens_fc(modules):
#     return A2_test_cases_aux.test_fc_10queens(modules[PROPAGATORS])

# @max_grade(5)
# def test_dwo_gac(modules):
#     return A2_test_cases_aux.test_DWO_GAC(modules[PROPAGATORS])

# @max_grade(5)
# def test_dwo_fc(modules):
#     return A2_test_cases_aux.test_DWO_FC(modules[PROPAGATORS])

# @max_grade(1)
# def test_model_1_import(modules):
#     return A2_test_cases_aux.model_1_import(modules[MODELS])

# @max_grade(1)
# def test_model_2_import(modules):
#     return A2_test_cases_aux.model_2_import(modules[MODELS])

# @max_grade(1)
# def test_model_1_constraints_enum_rewscols(modules):
#     return A2_test_cases_aux.check_model_1_constraints_enum_rewscols(modules[MODELS])

# #TODO this doesn't do anything...
# @max_grade(1)
# def test_model_1_constraints_enum_ineqs(modules):
#     return A2_test_cases_aux.check_model_1_constraints_enum_rewscols(modules[MODELS])

# #TODO this doesn't do anything...
# @max_grade(1)
# def test_model_2_constraints_enum_ineqs(modules):
#     return A2_test_cases_aux.check_model_2_constraints_enum_rewscols(modules[MODELS])

# @max_grade(1)
# def test_model_2_constraints_enum_rewscols(modules):
#     return A2_test_cases_aux.check_model_2_constraints_enum_rewscols(modules[MODELS])

# @max_grade(1)
# def test_model_1_constraints_FC(modules):
#     return A2_test_cases_aux.check_model_1_constraints_FC(modules[MODELS])

# @max_grade(1)
# def test_model_2_constraints_FC(modules):
#     return A2_test_cases_aux.check_model_2_constraints_FC(modules[MODELS])

# @max_grade(1)
# def test_model_1_constraints_GAC(modules):
#     return A2_test_cases_aux.check_model_1_constraints_GAC(modules[MODELS])

# @max_grade(1)
# def test_model_2_constraints_GAC(modules):
#     return A2_test_cases_aux.check_model_2_constraints_GAC(modules[MODELS])

# @max_grade(4)
# def test_unsat_problem_model_1(modules):
#     return A2_test_cases_aux.test_UNSAT_problem_model_1(modules[MODELS])

# @max_grade(4)
# def test_unsat_problem_model_2(modules):
#     return A2_test_cases_aux.test_UNSAT_problem_model_2(modules[MODELS])

# @max_grade(2)
# def test_binary_constraint_model_1(modules):
#     return A2_test_cases_aux.check_binary_constraint_model_1(modules[MODELS])

# @max_grade(2)
# def test_nary_constraint_model_2(modules):
#     return A2_test_cases_aux.check_nary_constraint_model_2(modules[MODELS])

# @max_grade(4)
# def test_out_of_domain_tuple_model_1(modules):
#     return A2_test_cases_aux.check_out_of_domain_tuple(modules[MODELS].futoshiki_csp_model_1, "model 1")

# @max_grade(4)
# def test_out_of_domain_tuple_model_2(modules):
#     return A2_test_cases_aux.check_out_of_domain_tuple(modules[MODELS].futoshiki_csp_model_2, "model 2")

# @max_grade(5)
# def test_big_problem_model_1(modules):
#     return A2_test_cases_aux.test_big_problem(modules[MODELS].futoshiki_csp_model_1, "model 1")

# @max_grade(5)
# def test_big_problem_model_2(modules):
#     return A2_test_cases_aux.test_big_problem(modules[MODELS].futoshiki_csp_model_2, "model 2")

# @max_grade(5)
# def test_full_run_model_1(modules):
#     return A2_test_cases_aux.test_full_run(modules[MODELS].futoshiki_csp_model_1, modules[PROPAGATORS], "model 1")

# @max_grade(5)
# def test_full_run_model_2(modules):
#     return A2_test_cases_aux.test_full_run(modules[MODELS].futoshiki_csp_model_2, modules[PROPAGATORS], "model 2")


