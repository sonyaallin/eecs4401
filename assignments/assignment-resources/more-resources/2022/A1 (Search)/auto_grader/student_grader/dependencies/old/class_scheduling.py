LEC = 'LEC'
TUT = 'TUT'
NOCLASS = 'NOCLASS'

class ScheduleProblem:
  '''Class to hold an instance of the class scheduling problem.
      defined by the following data items
      a) A list of courses to take

      b) A list of classes with their course codes, buildings, time slots, class types, 
        and sections. It is specified as a string with the following pattern:
        <course_code>-<building>-<time_slot>-<class_type>-<section>

        An example of a class would be: CSC384-BA-10-LEC-01
        Note: Time slot starts from 1. Ensure you don't make off by one error!

      c) A list of buildings

      d) A positive integer N indicating number of time slots

      e) A list of pairs of buildings (b1, b2) such that b1 and b2 are close 
        enough for two consecutive classes.

      f) A positive integer K specifying the minimum rest frequency. That is, 
        if K = 4, then at least one out of every contiguous sequence of 4 
        time slots must be a NOCLASS.

      See class_scheduling.py for examples of the use of this class.
  '''

  def __init__(self, courses, classes, buildings, num_time_slots, connected_buildings,
                min_rest_frequency):
    # do some data checks
    for class_info in classes:
      info = class_info.split('-')
      if info[0] not in courses:
        print("ScheduleProblem Error, classes list contains a non-course", info[0])
      if info[3] not in [LEC, TUT]:
        print("ScheduleProblem Error, classes list contains a non-lecture and non-tutorial", info[1])
      if int(info[2]) > num_time_slots or int(info[2]) <= 0:
        print("ScheduleProblem Error, classes list  contains an invalid class time", info[2])
      if info[1] not in buildings:
        print("ScheduleProblem Error, classes list  contains a non-building", info[3])

    for (b1, b2) in connected_buildings:
      if b1 not in buildings or b2 not in buildings:
        print("ScheduleProblem Error, connected_buildings contains pair with non-building (", b1, ",", b2, ")")

    if num_time_slots <= 0:
      print("ScheduleProblem Error, num_time_slots must be greater than 0")

    if min_rest_frequency <= 0:
      print("ScheduleProblem Error, min_rest_frequency must be greater than 0")

    # assign variables
    self.courses = courses
    self.classes = classes
    self.buildings = buildings
    self.num_time_slots = num_time_slots
    self._connected_buildings = dict()
    self.min_rest_frequency = min_rest_frequency

    # now convert connected_buildings to a dictionary that can be index by building.
    for b in buildings:
      self._connected_buildings.setdefault(b, [b])

    for (b1, b2) in connected_buildings:
      self._connected_buildings[b1].append(b2)
      self._connected_buildings[b2].append(b1)

  # some useful access functions
  def connected_buildings(self, building):
    '''Return list of buildings that are connected from specified building'''
    return self._connected_buildings[building]


# test-sequence--one solution (only one legal sequencing)
c1 = ScheduleProblem(
    # courses
    ['CSC108'],
    # classes
    ['CSC108-BA-2-LEC-01', 'CSC108-BA-3-TUT-01'],
    # buildings
    ['BA'],
    # number of time slots
    3,
    # connected buildings
    [],
    # min rest frequency
    3
)

# no solution due to lecture/tutorial order
c2 = ScheduleProblem(
    # courses
    ['CSC108', 'CSC165'],
    # classes
    ['CSC108-SF-2-LEC-01',
        'CSC108-SF-1-TUT-01',
        'CSC165-MP-4-LEC-01',
        'CSC165-MP-5-TUT-01'],
    # buildings
    ['SF', 'MP'],
    # number of time slots
    5,
    # connected building
    [('SF', 'MP')],
    # min rest frequency
    5
)

# no solution due to building connectivity
c3 = ScheduleProblem(
    # courses
    ['CSC108', 'CSC165'],
    # classes
    ['CSC108-SF-1-LEC-01',
        'CSC108-SF-2-TUT-01',
        'CSC165-MP-3-LEC-01',
        'CSC165-MP-4-TUT-01'],
    # buildings
    ['SF', 'MP'],
    # number of time slots
    5,
    # connected building
    [],
    # min rest frequency
    5
)

# no solution due to frequency
c4 = ScheduleProblem(
    # courses
    ['CSC108', 'CSC165'],
    # classes
    ['CSC108-SF-1-LEC-01',
        'CSC108-SF-2-TUT-01',
        'CSC165-MP-3-LEC-01',
        'CSC165-MP-4-TUT-01'],
    # buildings
    ['SF', 'MP'],
    # number of time slots
    5,
    # connected building
    [('SF', 'MP')],
    # min rest frequency
    3
)

# multiple solutions
c5 = ScheduleProblem(
    # courses
    ['CSC108'],
    # classes
    ['CSC108-BA-1-LEC-01', 'CSC108-BA-2-LEC-02', 'CSC108-BA-3-TUT-01'],
    # buildings
    ['BA'],
    # number of time slots
    3,
    # connected buildings
    [],
    # min rest frequency
    3
)

c6 = ScheduleProblem(
    # courses
    ['CSC108', 'CSC165', 'MAT137'],
    # classes
    ['CSC108-BA-1-LEC-01',
        'CSC108-MP-2-LEC-02',
        'CSC108-SF-4-TUT-01',
        'CSC165-BA-3-LEC-01',
        'CSC165-MP-5-LEC-02',
        'CSC165-MP-6-TUT-01',
        'CSC165-MP-8-TUT-02',
        'MAT137-SF-7-LEC-01',
        'MAT137-BA-5-LEC-02',
        'MAT137-SF-10-TUT-01',
        'MAT137-SF-9-TUT-02'],
    # buildings
    ['BA', 'MP', 'SF'],
    # number of time slots
    10,
    # connected buildings
    [('BA', 'MP'), ('BA', 'SF')],
    # min rest frequency
    6
)


def get_class_info(class_section):
    space_index = class_section.index(' ')
    return class_section[:space_index], class_section[space_index + 1:]


def check_schedule_solution(problem, schedule):
    if len(schedule) == 0:
        return False
    tests = [check_valid_classes,
             check_consecutive_classes_buildings, check_taken_courses_once,
             check_resting]

    for test in tests:
        if not test(problem, schedule):
            return False

    return True


def check_valid_classes(problem, schedule):
    for time_slot in schedule:
        if time_slot == NOCLASS:
            continue
        if time_slot not in problem.classes:
            print(
                "Error solution invalid, non-existent class {} in the schedule".format(c))
            return False
    return True


def check_consecutive_classes_buildings(problem, schedule):
    for i, _ in enumerate(schedule):
        if i + 1 == len(schedule) or schedule[i] == NOCLASS or schedule[i + 1] == NOCLASS:
            continue

        building_1 = schedule[i].split('-')[1]
        building_2 = schedule[i + 1].split('-')[1]
        if building_2 not in problem.connected_buildings(building_1):
            print("Error solution invalid, consecutive classes {}, {} in the schedule is too far apart".format(
                schedule[i], schedule[i + 1]))
            return False

    return True


def check_taken_courses_once(problem, schedule):
    checklist = dict()
    for course in problem.courses:
        checklist[course] = [0, 0]

    for class_1 in schedule:
        if class_1 == NOCLASS:
            continue
        class_1_info = class_1.split('-')
        if class_1_info[0] not in checklist:
            print("Error solution invalid, class {} should not be taken by the student".format(
                course_1))
            return False

        if class_1_info[3] == LEC:
            checklist[class_1_info[0]][0] += 1

        if class_1_info[3] == TUT:
            if checklist[class_1_info[0]][0] == 0:
                print("Error solution invalid, tutorial for class {} should not be taken before lecture".format(
                    class_1))
                return False
            checklist[class_1_info[0]][1] += 1

    if any([any([checklist[key][0] > 1, checklist[key][1] > 1]) for key in checklist]):
        print("Error solution invalid, class {} is taken more than once for some class type".format(class_1))
        return False

    for key in checklist:
        if checklist[key][0] + checklist[key][1] < 2:
            print(
                "Error solution invalid, class {} is taken less than once for some class type".format(key))
            return False
    return True


def check_resting(problem, schedule):
    if len(schedule) < problem.min_rest_frequency:
        return True
    for i in range(len(schedule) - problem.min_rest_frequency + 1):
        count = 0
        for j in range(problem.min_rest_frequency):
            if schedule[i + j] == NOCLASS:
                count += 1
        if count == 0:
            print("Error solution invalid, student takes to many classes before resting")
            return False
    return True
