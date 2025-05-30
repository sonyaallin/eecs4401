#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bnetbase import *
from solution_complete import *


# In[2]:


test_multiply = True
test_restrict = True
test_sum = True
test_normalize = True
test_ve = True
test_nb = True


#  E,B,S,w,G example 

# In[3]:


E, B, S, G, W = Variable('E', ['e', '-e']), Variable('B', ['b', '-b']), Variable('S', ['s', '-s']), Variable('G', ['g', '-g']), Variable('W', ['w', '-w'])
FE, FB, FS, FG, FW = Factor('P(E)', [E]), Factor('P(B)', [B]), Factor('P(S|E,B)', [S, E, B]), Factor('P(G|S)', [G,S]), Factor('P(W|S)', [W,S])


# In[4]:


FE.add_values([['e',0.1], ['-e', 0.9]])
FB.add_values([['b', 0.1], ['-b', 0.9]])
FS.add_values([['s', 'e', 'b', .9], ['s', 'e', '-b', .2], ['s', '-e', 'b', .8],['s', '-e', '-b', 0],
                 ['-s', 'e', 'b', .1], ['-s', 'e', '-b', .8], ['-s', '-e', 'b', .2],['-s', '-e', '-b', 1]])
FG.add_values([['g', 's', 0.5], ['g', '-s', 0], ['-g', 's', 0.5], ['-g', '-s', 1]])
FW.add_values([['w', 's', 0.8], ['w', '-s', .2], ['-w', 's', 0.2], ['-w', '-s', 0.8]])


# In[5]:


SampleBN = BN('SampleBN', [E,B,S,G,W], [FE,FB,FS,FG,FW])


# In[6]:


def test_multiply_fun():
    print("\nMultiply Factors Test ... ", end='')
    factor = multiply_factors([FB, FE])
    tests = []
    values = []
    for e_val in E.domain():
      for b_val in B.domain():
        try:
          value = factor.get_value([e_val, b_val])
          values.append(value)
        except ValueError:
          value = factor.get_value([b_val, e_val])
          values.append(value)
        tests.append(value == FE.get_value([e_val])*FB.get_value([b_val]))
    if all(tests):
      print("passed.")
    else:
      print("failed.")      
    print('P(e,b) = {} P(-e,b) = {} P(e,-b) = {} P(-e,-b) = {}'.format(values[0], values[1], values[2], values[3]))


# In[7]:


def test_sum_fun():
    print("\nSum Out Variable Test ....", end='')
    factor = sum_out_variable(FS, E)
    values = (factor.get_value(["s", "b"]), factor.get_value(["s", "-b"]), factor.get_value(["-s", "b"]), factor.get_value(["-s", "-b"]))
    tests = (abs(values[0] - 1.7) < 0.001, abs(values[1] - 0.2) < 0.001, abs(values[2] - 0.3) < 0.001, abs(values[3] - 1.8) < 0.001)
    if all(tests):
      print("passed.")
    else:
      print("failed.")
    print('P(S = s | B = b) = {} P(S = s | B = -b) = {} P(S = -s | B = b) = {} P(S = -s | B = -b) = {}'.format(values[0], values[1], values[2], values[3]))


# In[8]:


def test_restrict_fun():
    print("\nRestrict Factor Test ...", end='')
    factor = restrict_factor(FG, S, 's')
    value = factor.get_value_at_current_assignments()
    if value == 0.5:
      print("passed.")
    else:
      print("failed.")
    print('P(G|S=s) = {}'.format(value))


# In[9]:


def test_normalize_fun():
    
    print("\nNormalize Test .... ", end='')
    normalized_nums = normalize([i for i in range(0,-5,-1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
      print("passed.")
    else:
      print("failed.")
    print('{} when normalized to {} sum to {}'.format([i for i in range(0,-5,-1)], normalized_nums, norm_sum))


# In[10]:


def test_ve_fun():
    print("\nVE Tests .... ")
    print("Test 1 ....", end = '')
    S.set_evidence('-s')
    W.set_evidence('w')
    probs3 = VE(SampleBN, G, [S,W])
    S.set_evidence('-s')
    W.set_evidence('-w')
    probs4 = VE(SampleBN, G, [S,W])
    if probs3[0] == 0.0 and probs3[1] == 1.0 and probs4[0] == 0.0 and probs4[1] == 1.0:
      print("passed.")
    else:
      print("failed.") 
    print('P(g|-s,w) = {} P(-g|-s,w) = {} P(g|-s,-w) = {} P(-g|-s,-w) = {}'.format(probs3[0],probs3[1],probs4[0],probs4[1]))
    print("Test 2 ....", end = '')
    W.set_evidence('w')
    probs1 = VE(SampleBN, G, [W])
    W.set_evidence('-w')
    probs2 = VE(SampleBN, G, [W])
    if abs(probs1[0] - 0.15265998457979954) < 0.0001 and abs(probs1[1] - 0.8473400154202004) < 0.0001 and abs(probs2[0] - 0.01336753983256819) < 0.0001 and abs(probs2[1] - 0.9866324601674318) < 0.0001:
      print("passed.")
    else:
      print("failed.")      
    print('P(g|w) = {} P(-g|w) = {} P(g|-w) = {} P(-g|-w) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))


# In[11]:


def test_nb_fun():
    print("\nNaive Bayes Model Test .... ", end='')
    if abs(Explore()[0] - 95.39995929167515) < 0.0001:
        print("Q1 passed.")
    else:
        print("Q1 failed.")
    if abs(Explore()[1] - 0.0000) < 0.0001:
        print("Q2 passed.")
    else:
        print("Q2 failed.")
    if abs(Explore()[2] - 59.654178674351584) < 0.0001:
        print("Q3 passed.")
    else:
        print("Q3 failed.")
    if abs(Explore()[3] - 67.36053288925895) < 0.0001:
        print("Q4 passed.")
    else:
        print("Q4 failed.")
    if abs(Explore()[4] - 7.062894361897008) < 0.0001:
        print("Q5 passed.")
    else:
        print("Q5 failed.")
    if abs(Explore()[5] - 23.67202128707992) < 0.0001:
        print("Q6 passed.")
    else:
        print("Q6 failed.")


# In[12]:


if __name__ == '__main__':
            if test_multiply: test_multiply_fun()
            if test_sum: test_sum_fun()
            if test_restrict: test_restrict_fun()
            if test_normalize: test_normalize_fun()
            if test_ve: test_ve_fun()
            if test_nb: test_nb_fun()

