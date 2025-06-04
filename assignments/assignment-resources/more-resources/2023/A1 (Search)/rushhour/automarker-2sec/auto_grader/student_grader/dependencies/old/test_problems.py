"""20 Snowman test problems.
"""
from snowman import SnowmanState

def generate_coordinate_rect(x_start, x_finish, y_start, y_finish):
    """
    Generate tuples for coordinates in rectangle (x_start, x_finish) -> (y_start, y_finish)
    """
    coords = []
    for i in range(x_start, x_finish):
        for j in range(y_start, y_finish):
            coords.append((i, j))
    return coords


PROBLEMS = (
    #Problem 0,
    SnowmanState("START", 0, None, 4, 4, # dimensions
                 (0, 3), #robot
                 {(1, 2): 0, (1, 1): 1, (2, 1): 2}, #snowballs
                 frozenset(((0, 0), (3, 3))), #obstacles
                 (1, 3), #destination                 
                 ),
    # Problem 1,
    SnowmanState("START", 0, None, 5, 4, # dimensions
             (0, 3), #robot
             {(2, 2): 0, (3, 1): 1, (1, 2): 2}, #snowballs
             frozenset(((0, 0), (4, 0), (2, 3), (3, 3), (4, 3))), #obstacles
             (3, 2), #destination                 
             ),    
    # Problem 2,
    SnowmanState("START", 0, None, 6, 4, # dimensions
             (5, 3), #robot
             {(2, 1): 0, (3, 1): 1, (3, 2): 2}, #snowballs
             frozenset(((0, 0), (5, 0), (0, 3), (1, 3), (2, 3), (3, 3))), #
             (2, 2), #destination                     
             ),
    # Problem 3
    SnowmanState("START", 0, None, 5, 5, # dimensions
                 (2, 1), # robot
                 {(2, 3): 0, (1, 2): 1, (3, 2): 2}, #snowballs
                 frozenset(((1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4))), #obstacles
                 (4, 4), #destination                       
                 ),
    # Problem 4
    SnowmanState("START", 0, None, 6, 6, # dimensions
                 (4, 0), #robot
                 {(3, 1): 0, (3, 2): 1, (3, 3): 2}, #snowballs
                 frozenset(((2, 0), (2, 1), (2, 3), (2, 4))), #obstacles
                 (2, 2), #destination                       
                 ),
    # Problem 5, 
    SnowmanState("START", 0, None, 7, 7, # dimensions
                 (4, 0), #robot
                 {(3, 1): 0, (3, 2): 1, (1, 3): 2}, #snowballs
                 frozenset(((2, 0), (2, 1), (2, 3), (2, 4), (2, 5))), #obstacles
                 (2, 2), #destination                      
                 ),
    # Problem 6,
    SnowmanState("Start", 0, None, 6, 7, # dimensions
        (5, 5), #robot
        {(3, 3): 0, (3, 4): 1, (3, 5): 2}, # snowballs
        frozenset(((1, 2), (1, 3), (1, 4), (1, 5),(1, 6), (2, 2), (5, 1), (5, 0))), # obstacles
        (2, 3), #destination              
        ),    
    # Problem 7, 
    SnowmanState("Start", 0, None, 6, 4, # dimensions
        (2, 2),
        {(1, 1): 0, (2, 1): 1, (4, 1): 2}, # snowballs
        frozenset(((0, 0), (2, 0), (3, 0), (0, 3), (1, 3), (2, 3))), # obstacles
        (1, 0), #destination             
        ),
    # Problem 8,
    SnowmanState("Start", 0, None, 6, 7, # dimensions
        (1, 0), # robot
        {(2, 1): 0, (1, 4): 1, (4, 5): 2}, # snowballs
        frozenset(((0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (3, 2), (3, 3), (4, 4),
        (3, 0), (4, 0), (5, 0), (5, 1), (5, 2))), # obstacles
        (2, 2), #destination             
        ),
    #Problem 9,
    SnowmanState("START", 0, None, 6, 4, # dimensions
         (4, 3), #robot
         {(3, 1): 0, (3, 2): 2, (4, 2): 1}, #snowballs
         frozenset((generate_coordinate_rect(4, 6, 0, 1)
                   + generate_coordinate_rect(0, 3, 3, 4))), #obstacles
         (3, 3), #destination
         ),   

    #Problem 10
    SnowmanState("START", 0, None, 6, 4, # dimensions
         (5, 2), #robot
         {(3, 1): 0, (2, 2): 1, (3, 2): 2}, #snowballs
         frozenset((generate_coordinate_rect(4, 6, 0, 1)
                   + generate_coordinate_rect(0, 3, 3, 4))), #obstacles
         (5, 1), #destination
         ),
    #Problem 11 
    SnowmanState("START", 0, None, 6, 5, # dimensions
         (5, 2), #robot
         {(3, 1): 0, (3, 2): 1, (3, 3): 2}, #snowballs
         frozenset((generate_coordinate_rect(4, 6, 0, 1)
                    + generate_coordinate_rect(3, 6, 4, 5))
                    + [(1, 1), (1, 3)]), #obstacles
         (5, 1), #destination
         ),  
    # Problem 12
    SnowmanState("START", 0, None, 6, 4, # dimensions
         (5, 3), #robot
         {(3, 1): 0, (2, 2): 1, (3, 2): 2}, #snowballs
         frozenset((generate_coordinate_rect(4, 6, 0, 1)
                   + generate_coordinate_rect(0, 3, 3, 4))), #obstacles
         (2, 1), #destination          
         ),

    #Problem 13 
    SnowmanState("START", 0, None, 8, 6, # dimensions
         (1, 2), #robot
         {(1, 3): 0, (2, 3): 1, (3, 3): 2}, #snowballs
         frozenset((generate_coordinate_rect(0, 7, 0, 2) + [(0, 2), (6, 2), (7, 5)]
         + generate_coordinate_rect(0, 5, 5, 6))), #obstacles
         (7, 0), #destination
         ),

    # Problem 14
    SnowmanState("START", 0, None, 8, 8, # dimensions
        (0, 5), #robot
        {(1, 5): 0, (3, 5): 1, (4, 5): 2}, # snowballs
        frozenset(((0, 4), (1, 4), (2, 4), (3, 4))), # obstacles
        (0, 2), #destination             
        ),

    # Problem 15
    SnowmanState("Start", 0, None, 8, 7, # dimensions
        (5, 5), # robot
        {(1, 3): 1, (3, 2): 0, (2, 1): 2}, # snowballs
        frozenset(((0, 4), (1, 4), (2, 4), (3, 4), (5, 4), (1, 5), (1, 6), (7, 6), (7, 5),
        (7, 4), (7, 3), (7, 2), (2, 2), (4, 2), (5, 2), (5, 1))), # obstacles
        (2, 3), #destination             
        ),    

    # Problem 16
    SnowmanState("START", 0, None, 9, 6, # dimensions
        (0, 0), #robot
        {(2, 1): 0, (6, 4): 1, (6, 3): 2}, # snowballs
        frozenset((generate_coordinate_rect(2, 7, 2, 3) + generate_coordinate_rect(2, 3, 2, 6))), # obstacles
        (2, 0), #destination              
        ),
    # Problem 17
    SnowmanState("START", 0, None, 10, 7, # dimensions
        (0, 0), #robot
        {(5, 3): 0, (7, 4): 1, (7, 5): 2}, # snowballs
        frozenset((generate_coordinate_rect(2, 8, 2, 3) + generate_coordinate_rect(2, 3, 2, 7))), # obstacles
        (2, 0), #destination              
        ),

    # Problem 18
    SnowmanState("Start", 0, None, 6, 5, # dimensions
        (1, 4), # robot
        {(2, 2): 0, (1, 2): 1, (4, 1): 2}, # snowballs
        frozenset(((1, 3), (0, 3))), # obstacles
        (0, 4), #destination              
        ),
    # Problem 19
    SnowmanState("Start", 0, None, 7, 6, # dimensions
        (1, 0),
        {(1, 1): 0, (2, 3): 1, (2, 4): 2},
        frozenset(((3, 0), (3, 1), (3, 2), (3, 4), (3, 5),)),
        (4, 5), #destination              
        ),    

)

EASY_PROBLEMS = (
SnowmanState("START", 0, None, 8, 10, (2, 2), {(2, 1): 0, (4, 3): 1, (1, 8): 2}, frozenset(((2, 3), (3, 0), (5, 1), (1, 3), (1, 2), (4, 5))), (4, 1),),
SnowmanState("START", 0, None, 6, 4, (2, 0), {(1, 2): 0, (4, 1): 1, (3, 2): 2}, frozenset(((2, 3), (2, 2))), (5, 1),),
SnowmanState("START", 0, None, 5, 5, (0, 2), {(1, 3): 0, (3, 3): 1, (3, 1): 2}, frozenset(((4, 1),)), (0, 3),),
SnowmanState("START", 0, None, 10, 7, (9, 2), {(1, 1): 0, (7, 2): 1, (2, 1): 2}, frozenset(((2, 3), (3, 6), (4, 1), (4, 3), (8, 0))), (0, 3),),
SnowmanState("START", 0, None, 8, 8, (6, 5), {(4, 4): 0, (6, 3): 1, (1, 6): 2}, frozenset(((2, 0), (3, 4), (0, 2), (6, 4))), (7, 6),),
SnowmanState("START", 0, None, 10, 4, (8, 3), {(2, 1): 0, (8, 1): 1, (5, 1): 2}, frozenset(((5, 0), (5, 2), (0, 1), (5, 3), (6, 2), (4, 3))), (4, 1),),
SnowmanState("START", 0, None, 10, 10, (0, 7), {(2, 7): 0, (7, 2): 1, (5, 3): 2}, frozenset(((4, 5), (8, 6), (7, 8), (5, 7), (2, 4), (3, 5), (7, 4), (3, 0), (7, 1), (4, 6))), (2, 5),),
SnowmanState("START", 0, None, 7, 8, (3, 1), {(2, 6): 0, (3, 2): 1, (4, 6): 2}, frozenset(((5, 1), (5, 5), (3, 6), (5, 2))), (0, 4),),
SnowmanState("START", 0, None, 7, 6, (4, 5), {(3, 2): 0, (2, 1): 1, (4, 4): 2}, frozenset(((2, 0), (6, 0))), (3, 4),),
SnowmanState("START", 0, None, 8, 10, (6, 1), {(6, 3): 0, (2, 5): 1, (2, 3): 2}, frozenset(((6, 2), (1, 5), (5, 6), (3, 5), (5, 8), (3, 0), (7, 4), (5, 2), (1, 1), (3, 1))), (1, 2),),
)


MEDIUM_PROBLEMS = (
SnowmanState("START", 0, None, 9, 7, (5, 2), {(3, 4): 0, (2, 2): 1, (5, 3): 2}, frozenset(((0, 3), (5, 5), (8, 2), (7, 4), (1, 2), (0, 5), (8, 4), (5, 1), (4, 3), (6, 3), (4, 0), (6, 6), (6, 0))), (6, 2),),
SnowmanState("START", 0, None, 7, 7, (4, 4), {(4, 2): 0, (1, 3): 1, (5, 2): 2}, frozenset(((4, 1), (4, 3), (0, 3), (6, 5), (5, 4), (4, 6), (6, 0))), (2, 5),),
SnowmanState("START", 0, None, 10, 10, (3, 6), {(1, 2): 0, (3, 5): 1, (3, 4): 2}, frozenset(((5, 9), (4, 1), (7, 9), (3, 8), (7, 2), (2, 3), (1, 7), (0, 0), (1, 5), (6, 9), (6, 4), (1, 4), (9, 2), (4, 6), (6, 3), (5, 2), (2, 9), (1, 6))), (0, 4),),
SnowmanState("START", 0, None, 10, 4, (3, 3), {(4, 1): 0, (3, 2): 1, (8, 2): 2}, frozenset(((7, 3), (6, 3), (2, 2), (6, 0), (7, 2), (0, 1), (6, 2))), (3, 1),),
SnowmanState("START", 0, None, 9, 7, (6, 2), {(7, 2): 0, (6, 4): 1, (3, 3): 2}, frozenset(((1, 6), (8, 4), (4, 0), (2, 5), (2, 0), (1, 1), (8, 3), (4, 5), (1, 2))), (7, 3),),
SnowmanState("START", 0, None, 10, 4, (7, 1), {(1, 1): 0, (4, 2): 1, (5, 1): 2}, frozenset(((8, 1), (7, 2), (9, 2), (5, 3), (4, 1), (0, 3), (3, 1), (9, 0), (9, 3), (0, 0))), (2, 1),),
SnowmanState("START", 0, None, 5, 9, (4, 7), {(2, 2): 0, (3, 6): 1, (2, 3): 2}, frozenset(((1, 2), (3, 1), (3, 8), (3, 5), (0, 6), (4, 4))), (2, 4),),
SnowmanState("START", 0, None, 8, 8, (5, 2), {(5, 3): 0, (0, 2): 1, (5, 4): 2}, frozenset(((2, 4), (6, 1), (1, 7), (7, 6), (3, 2), (4, 3), (3, 6), (3, 7), (4, 7), (7, 2))), (0, 3),),
SnowmanState("START", 0, None, 9, 8, (0, 7), {(2, 1): 0, (2, 5): 1, (3, 1): 2}, frozenset(((4, 7), (6, 7), (1, 6), (8, 1), (2, 0), (4, 4), (6, 1), (0, 3), (7, 6), (0, 2), (7, 0), (8, 7), (1, 5), (7, 2), (5, 4), (0, 4))), (1, 1),),
SnowmanState("START", 0, None, 9, 6, (0, 5), {(4, 2): 0, (3, 4): 1, (1, 2): 2}, frozenset(((8, 4), (6, 1), (4, 5), (2, 1), (8, 0), (8, 5), (5, 1), (6, 2), (5, 0), (7, 3), (6, 3), (3, 2), (6, 0))), (0, 2),),
)



HARD_PROBLEMS = (
SnowmanState("START", 0, None, 9, 6, (4, 5), {(4, 2): 0, (6, 1): 1, (3, 4): 2}, frozenset(((6, 4), (7, 3), (8, 3), (8, 2), (6, 3), (7, 4), (6, 2), (7, 5), (7, 2), (8, 5), (6, 5), (8, 4), (2, 3), (1, 3), (5, 5), (1, 1), (1, 2), (0, 5))), (5, 4),),
SnowmanState("START", 0, None, 8, 8, (6, 0), {(1, 6): 0, (2, 4): 1, (2, 2): 2}, frozenset(((3, 2), (5, 4), (6, 7), (3, 3), (6, 6), (5, 6), (7, 6), (5, 7), (4, 4), (7, 7), (5, 2), (4, 3), (4, 2), (3, 4), (5, 3), (6, 5), (7, 1), (5, 0), (1, 2), (1, 7), (7, 3))), (1, 4),),
SnowmanState("START", 0, None, 10, 4, (1, 0), {(3, 1): 0, (6, 1): 1, (8, 1): 2}, frozenset(((1, 2), (0, 1), (3, 2), (1, 3), (3, 3), (1, 1), (2, 3), (2, 2), (0, 2), (9, 0), (0, 3), (7, 0), (5, 3), (8, 0))), (7, 1),),
SnowmanState("START", 0, None, 8, 8, (6, 2), {(1, 5): 0, (4, 3): 1, (3, 4): 2}, frozenset(((3, 0), (6, 1), (3, 1), (6, 0), (2, 1), (2, 0), (5, 0), (5, 1), (1, 0), (4, 1), (1, 1), (4, 0), (3, 6), (7, 6), (6, 4), (0, 3), (5, 5))), (5, 4),),
SnowmanState("START", 0, None, 9, 5, (7, 0), {(3, 2): 0, (7, 2): 1, (5, 2): 2}, frozenset(((0, 1), (1, 2), (1, 3), (0, 2), (0, 3), (1, 1), (7, 1), (6, 4), (4, 3), (2, 3), (1, 4), (4, 0))), (6, 1),),
SnowmanState("START", 0, None, 7, 8, (2, 4), {(4, 2): 0, (5, 4): 1, (1, 3): 2}, frozenset(((2, 7), (2, 6), (1, 4), (1, 5), (0, 5), (3, 6), (0, 4), (3, 7), (2, 5), (3, 5), (0, 0), (5, 7), (3, 2), (3, 4))), (4, 3),),
SnowmanState("START", 0, None, 10, 10, (0, 6), {(5, 5): 0, (3, 4): 1, (1, 5): 2}, frozenset(((6, 4), (9, 7), (6, 7), (6, 8), (6, 6), (7, 6), (9, 8), (7, 7), (8, 5), (9, 5), (7, 4), (7, 5), (8, 8), (8, 7), (9, 4), (9, 6), (8, 6), (7, 8), (6, 5), (8, 4), (1, 8), (4, 1), (2, 6), (3, 0), (7, 3), (4, 2), (5, 0), (1, 2))), (3, 5),),
SnowmanState("START", 0, None, 8, 7, (5, 3), {(0, 3): 0, (4, 2): 1, (2, 2): 2}, frozenset(((7, 3), (5, 5), (6, 6), (5, 6), (7, 6), (6, 3), (7, 5), (6, 2), (7, 2), (6, 5), (3, 3), (7, 1), (2, 6), (3, 4))), (0, 1),),
SnowmanState("START", 0, None, 6, 10, (5, 9), {(4, 7): 0, (1, 6): 1, (3, 5): 2}, frozenset(((0, 1), (1, 2), (1, 3), (2, 9), (2, 8), (3, 8), (1, 8), (1, 1), (3, 9), (1, 9), (0, 3), (0, 2), (3, 4), (3, 1), (4, 9), (2, 6), (0, 4))), (4, 5),),
SnowmanState("START", 0, None, 6, 10, (3, 1), {(4, 4): 0, (3, 3): 1, (3, 4): 2}, frozenset(((2, 7), (2, 6), (2, 9), (2, 8), (0, 7), (0, 6), (1, 8), (1, 6), (1, 9), (1, 7), (0, 9), (0, 8), (3, 9), (5, 2), (5, 8), (0, 0), (0, 2), (4, 3), (4, 5))), (1, 4),),
SnowmanState("START", 0, None, 10, 9, (2, 2), {(6, 2): 0, (7, 3): 1, (4, 2): 2}, frozenset(((1, 3), (6, 6), (5, 6), (1, 6), (2, 5), (0, 3), (6, 7), (3, 3), (4, 4), (1, 5), (3, 6), (0, 4), (2, 6), (4, 5), (1, 4), (0, 5), (2, 3), (3, 5), (4, 6), (5, 7), (0, 6), (4, 3), (3, 4), (2, 4), (1, 0), (2, 1), (8, 4), (9, 2), (6, 5), (0, 0))), (8, 3),),
SnowmanState("START", 0, None, 6, 10, (4, 4), {(2, 3): 0, (0, 3): 1, (1, 3): 2}, frozenset(((2, 6), (4, 6), (5, 5), (4, 5), (5, 6), (0, 6), (1, 5), (0, 5), (1, 6), (3, 6), (2, 5), (3, 5), (0, 1), (5, 9), (2, 0), (1, 8), (3, 3))), (0, 4),),
SnowmanState("START", 0, None, 10, 5, (8, 0), {(5, 2): 0, (4, 1): 1, (1, 3): 2}, frozenset(((6, 4), (5, 4), (7, 3), (8, 3), (9, 3), (6, 3), (7, 4), (9, 4), (8, 4), (5, 3), (1, 2), (9, 0), (4, 0))), (7, 2),),
SnowmanState("START", 0, None, 6, 9, (1, 8), {(4, 3): 0, (4, 6): 1, (1, 5): 2}, frozenset(((0, 1), (1, 2), (1, 3), (0, 2), (2, 1), (2, 3), (2, 2), (0, 3), (1, 1), (5, 2), (3, 4), (5, 7), (2, 5), (0, 7))), (2, 6),),
SnowmanState("START", 0, None, 7, 10, (5, 6), {(1, 3): 0, (1, 7): 1, (5, 5): 2}, frozenset(((5, 9), (4, 9), (2, 9), (4, 8), (2, 8), (3, 8), (1, 8), (3, 9), (1, 9), (0, 9), (0, 8), (5, 8), (5, 2), (1, 6), (3, 0), (4, 4), (1, 5))), (2, 7),),
SnowmanState("START", 0, None, 8, 8, (6, 0), {(5, 3): 0, (5, 6): 1, (3, 4): 2}, frozenset(((2, 7), (1, 3), (2, 6), (1, 4), (0, 7), (1, 5), (0, 6), (0, 5), (1, 6), (0, 4), (0, 3), (1, 7), (4, 1), (2, 3), (4, 2), (0, 1), (5, 0), (6, 3), (4, 4))), (7, 3),),
SnowmanState("START", 0, None, 7, 9, (2, 3), {(2, 1): 0, (5, 3): 1, (4, 1): 2}, frozenset(((2, 7), (4, 7), (2, 6), (1, 3), (4, 6), (0, 7), (1, 4), (0, 6), (1, 6), (0, 4), (3, 6), (1, 7), (3, 7), (0, 3), (4, 3), (6, 1), (2, 5), (6, 0))), (4, 4),),
SnowmanState("START", 0, None, 8, 4, (0, 1), {(2, 2): 0, (4, 1): 1, (2, 1): 2}, frozenset(((7, 3), (7, 1), (6, 1), (6, 3), (6, 2), (7, 2), (0, 0), (3, 0), (3, 2), (6, 0))), (3, 1),),
SnowmanState("START", 0, None, 8, 4, (4, 0), {(1, 1): 0, (1, 2): 1, (3, 2): 2}, frozenset(((7, 1), (6, 1), (6, 2), (5, 1), (5, 2), (7, 2), (4, 1), (0, 2), (6, 0), (5, 3))), (0, 1),),
SnowmanState("START", 0, None, 9, 9, (3, 3), {(5, 5): 0, (3, 4): 1, (2, 2): 2}, frozenset(((2, 7), (4, 7), (6, 7), (6, 8), (4, 8), (2, 8), (5, 7), (7, 7), (0, 7), (3, 8), (1, 8), (1, 7), (3, 7), (0, 8), (7, 8), (5, 8), (6, 1), (3, 2), (0, 4), (8, 0), (5, 1), (6, 2), (1, 6))), (1, 2),),
)

