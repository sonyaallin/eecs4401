from sys import argv
import re

test_case_start = "Test Case: \[function=(.*)\]\s*\[(.*)/(.*)\]"
test_case_start = re.compile(test_case_start)

test_case_end = "===================="
test_case_end = re.compile(test_case_end)

runtime_error = "(A runtime error occurred while .*): 'Traceback.*"
runtime_error = re.compile(runtime_error)

test_types = ["1. Initial state generation:",
              "2. Successor states generation:",
              "3. Goal check function:",
              "4. Hash function:",
              "5. Heuristic Function:",
              "6. Search:"]

test_to_types = {}

test_to_types["test_fval_function"] = test_types[0]
test_to_types["test_fval_function"] = test_types[0]

test_to_types["test_manhattan"] = test_types[1]
test_to_types["test_functions"] = test_types[1]
test_to_types["test_successors_empty_name"] = test_types[1]
test_to_types["test_successors_state_properties"] = test_types[1]
test_to_types["test_successors_long_vehicle"] = test_types[1]
test_to_types["test_successors_collision_similar_names"] = test_types[1]

test_to_types["test_goal_check_simple"] = test_types[2]
test_to_types["test_goal_check_blocked"] = test_types[2]
test_to_types["test_goal_through_boundary"] = test_types[2]
test_to_types["test_goal_multiple_goals"] = test_types[2]

test_to_types["test_hashable_state_basic_different"] = test_types[3]
test_to_types["test_hashable_state_basic_equal"] = test_types[3]
test_to_types["test_hashable_equivalent_states_with_different_properties"] = test_types[3]
test_to_types["test_hashable_with_vehicles_with_similar_names"] = test_types[3]

test_to_types["test_heuristic_simple"] = test_types[4]
test_to_types["test_heuristic_multiple_goal_cars"] = test_types[4]

test_to_types["test_search"] = test_types[5]
test_to_types["test_search_no_solution"] = test_types[5]

def write_errors(results_filename):
    results = open(results_filename)
    in_test = False
    test_type = None
    errors = {}
    for x in test_types:
        errors[x] = set()

    for line in results:
        l = line.strip()
        if in_test:
            if test_case_end.match(l):
                in_test = False
                continue
            else:
                error = runtime_error.match(l)
                if error:
                    errors[test_type].add(error.group(1))
                elif l:
                    errors[test_type].add(l)

        parsed = test_case_start.match(l)
        if parsed:
            in_test = True
            test_name = parsed.group(1)
            if test_name not in test_to_types:
                raise Exception()
            test_type = test_to_types[test_name]

    output = ""
    for test_type in test_types:
        output += test_type + "\n"
        for error in errors[test_type]:
            output += "    " + error + "\n"
        if not errors[test_type]:
            output += "    [none]\n"
    return output

if __name__=="__main__":
    write_email(argv[1])
