
'''
LunarLockout Problem Set, for testing
'''
PROBLEMS = (
  #7x7 BOARDS: all are solveable
  #LunarLockoutState("START", 0, None, 7, ((4, 2), (1, 3), (6,3), (5,4)), ((6, 2))),
  #LunarLockoutState("START", 0, None, 7, ((2, 1), (4, 2), (2,6)), ((4, 6))),
  #LunarLockoutState("START", 0, None, 7, ((2, 1), (3, 1), (4, 1), (2,6), (4,6)), ((2, 0),(3, 0),(4, 0))),   
  #LunarLockoutState("START", 0, None, 7, ((1, 2), (0 ,2), (2 ,3), (4, 4), (2, 5)), ((2, 4),(3, 1),(4, 0))),   
  LunarLockoutState("START", 0, None, 7, ((3, 2), (0 ,2), (3 ,3), (4, 4), (2, 5)), ((1, 2),(3, 0),(4, 0))),   
  LunarLockoutState("START", 0, None, 7, ((3, 1), (0 ,2), (3 ,3), (4, 4), (2, 5)), ((1, 2),(3, 0),(4, 0))),   
  LunarLockoutState("START", 0, None, 7, ((2, 1), (0 ,2), (1 ,2), (6, 4), (2, 5)), ((2, 0),(3, 0),(4, 0))),   
  LunarLockoutState("START", 0, None, 7, ((3, 0), (4 ,0), (1 ,2), (5, 2), (6, 2)), ((2, 0),(0, 4),(4, 5))),

  #5x5 boards: all are solveable
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((0, 1))),
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((0, 2))),
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((0, 3))),
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 1))),  
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 2))),  
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 3))),  
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 4))),  
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 0))),  
  LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 1))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 3))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 4))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 0))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 1))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 2))),    
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 3))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 4))), 
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((4, 0))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((4, 1))),      
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((4, 3))),  

  LunarLockoutState("START", 0, None, 5, ((1, 1), (1, 3),(4,3)),((1, 0),(4,1))),
  LunarLockoutState("START", 0, None, 5, ((0, 0), (0, 2),(0,4),(2,0),(4,0)),((4, 4))),

  #5x5 boards: none are solveable
  LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 5))),
  LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((3, 5))),
  LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 5))),
  LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 6))),
  LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 6)))  

  #7x7 BOARDS: all are solveable
  #LunarLockoutState("START", 0, None, 7, ((4, 2), (1, 3), (6,3), (5,4)), ((6, 2))),
  #LunarLockoutState("START", 0, None, 7, ((2, 1), (4, 2), (2,6)), ((4, 6))),
  #LunarLockoutState("START", 0, None, 7, ((2, 1), (3, 1), (4, 1), (2,6), (4,6)), ((2, 0),(3, 0),(4, 0))),   
  #LunarLockoutState("START", 0, None, 7, ((1, 2), (0 ,2), (2 ,3), (4, 4), (2, 5)), ((2, 4),(3, 1),(4, 0))),   
  #LunarLockoutState("START", 0, None, 7, ((3, 2), (0 ,2), (3 ,3), (4, 4), (2, 5)), ((1, 2),(3, 0),(4, 0))),   
  #LunarLockoutState("START", 0, None, 7, ((3, 1), (0 ,2), (3 ,3), (4, 4), (2, 5)), ((1, 2),(3, 0),(4, 0))),   
  #LunarLockoutState("START", 0, None, 7, ((2, 1), (0 ,2), (1 ,2), (6, 4), (2, 5)), ((2, 0),(3, 0),(4, 0))),   
  #LunarLockoutState("START", 0, None, 7, ((3, 0), (4 ,0), (1 ,2), (5, 2), (6, 2)), ((2, 0),(0, 4),(4, 5)))
  
  #7x7 BOARDS: only ONE of the following is solveable
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 1))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((3, 1))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 1))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 2))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((3, 2))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 2))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 3))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 3))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 4))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((3, 4))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 4))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 5))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((3, 5))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 5))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((2, 6))),
  #LunarLockoutState("START", 0, None, 7, ((2, 0), (3, 0), (4 ,0), (1 ,2), (3, 6)), ((4, 6))),  
  
  #5x5 boards: all 19 are solveable
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((0, 1))),
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((0, 2))),
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((0, 3))),
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 1))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 2))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 3))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((1, 4))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 0))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 1))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 3))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((2, 4))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 0))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 1))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 2))),    
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 3))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((3, 4))), 
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((4, 0))),  
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((4, 1))),      
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (1, 0),(2,2),(4,2),(0,4),(4,4)),((4, 3))),  

  #5x5 boards: all are solveable
  #LunarLockoutState("START", 0, None, 5, ((1, 1), (1, 3),(4,3)),((1, 0),(4,1))),
  #LunarLockoutState("START", 0, None, 5, ((0, 0), (0, 2),(0,4),(2,0),(4,0)),((4, 4)))
)
