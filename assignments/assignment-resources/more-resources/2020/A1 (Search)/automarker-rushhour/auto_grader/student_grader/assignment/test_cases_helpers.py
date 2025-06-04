def comparable_state(state):
    vehicle_statuses = sorted(map(tuple, state.get_vehicle_statuses()))
    board_properties = tuple(state.get_board_properties())

    return (board_properties, tuple(vehicle_statuses))

def comparable_successors(state):
    return sorted(map(comparable_state, state.successors()))

def sorted_successors(state):
    successors = state.successors()

    successors.sort(key=lambda x: x.action)

    return successors

