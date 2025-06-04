# The tagger.py starter code for CSC384 A4.

import os
import sys
import getopt

import numpy as np
from collections import Counter
import math

UNIVERSAL_TAGS = [
    "VERB",
    "NOUN",
    "PRON",
    "ADJ",
    "ADV",
    "ADP",
    "CONJ",
    "DET",
    "NUM",
    "PRT",
    "X",
    ".",
]

N_tags = len(UNIVERSAL_TAGS)

def read_data_train(path):
    return [tuple(line.split(' : ')) for line in open(path, 'r').read().split('\n')[:-1]]

def read_data_test(path):
    return open(path, 'r').read().split('\n')[:-1]

def read_data_ind(path):
    return [int(line) for line in open(path, 'r').read().split('\n')[:-1]]

def write_results(path, results):
    with open(path, 'w') as f:
        f.write('\n'.join(results))

def train_HMM(train_file_name):
    """
    Estimate HMM parameters from the provided training data.

    Input: Name of the training files. Two files are provided to you:
            - file_name.txt: Each line contains a pair of word and its Part-of-Speech (POS) tag
            - fila_name.ind: The i'th line contains an integer denoting the starting index of the i'th sentence in the text-POS data above

    Output: Three pieces of HMM parameters stored in LOG PROBABILITIES :
 
            - prior:        - An array of size N_tags
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - A dictionary type containing tuples of (str, str) as keys
                            - Each key in the dictionary refers to a (TAG, WORD) pair
                            - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
                            - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    
    prior = [-100 for i in range(len(UNIVERSAL_TAGS))]
    initial_tags = list()
    transition_count = [[0 for i in range(len(UNIVERSAL_TAGS))] for j in range(len(UNIVERSAL_TAGS))]
    emission_count = dict()
    tag_count = dict()
    
    for i in range(len(pos_data)) :
        if i in sent_inds:
            initial_tags.append(pos_data[i][1])
        elif i > 0:
            transition_count[UNIVERSAL_TAGS.index(pos_data[i-1][1])][UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
        if (pos_data[i][1],pos_data[i][0]) in emission_count.keys():
            emission_count[(pos_data[i][1],pos_data[i][0])] += 1           
        else:
            emission_count[(pos_data[i][1],pos_data[i][0])] = 1  
        if pos_data[i][1] in tag_count.keys():
            tag_count[pos_data[i][1]] += 1
        else:
            tag_count[pos_data[i][1]] = 1
        
    
    c = Counter(initial_tags)
    for k in c.keys():
        prior[UNIVERSAL_TAGS.index(k)] = round(math.log(c[k]/len(sent_inds)),8)        
    transition = np.array([[None for i in range(len(UNIVERSAL_TAGS))] for j in range(len(UNIVERSAL_TAGS))])
    
    for i in range(len(UNIVERSAL_TAGS)):
        total_count = 0
        for j in range(len(UNIVERSAL_TAGS)):
            total_count += transition_count[i][j]
        for j in range(len(UNIVERSAL_TAGS)):
            if transition_count[i][j] == 0:
                transition[i][j] = float('-inf')
            else:
                transition[i][j] = round(math.log(transition_count[i][j])-math.log(total_count),8)
    
    emission = dict()
    
    for key in emission_count.keys():
        emission[key] = round(math.log(emission_count[key]/tag_count[key[0]]),8)
        if emission[key] >0:
            print(key,emission_count[key],tag_count[key[0]])
    prior = np.array(prior)
    
    return prior, transition, emission  

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    
    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    
    results = list()
    
    for i in range(len(sent_inds)):
        
        o_len = 0
        
        if i != len(sent_inds)-1:
            o_len = sent_inds[i+1]-sent_inds[i]
        else:
            o_len = len(pos_data)-sent_inds[i]
        
        prob_trellis = np.zeros((len(UNIVERSAL_TAGS),o_len))
        path_trellis = [[list() for i in range(o_len)] for j in range(len(UNIVERSAL_TAGS))]
        
        for j in range(len(UNIVERSAL_TAGS)):
            if (UNIVERSAL_TAGS[j],pos_data[sent_inds[i]]) not in emission.keys():
                emission[(UNIVERSAL_TAGS[j],pos_data[sent_inds[i]])]=-100
            
            prob_trellis[j][0] = prior[j] + emission[(UNIVERSAL_TAGS[j],pos_data[sent_inds[i]])]
            path_trellis[j][0].append(UNIVERSAL_TAGS[j])

        
        for j in range(1,o_len):
            for k in range(len(UNIVERSAL_TAGS)):
                max_prob = float('-inf')
                max_tag = None
                for l in range(len(UNIVERSAL_TAGS)):
                    if (UNIVERSAL_TAGS[k],pos_data[sent_inds[i]+j]) not in emission.keys():
                        emission[(UNIVERSAL_TAGS[k],pos_data[sent_inds[i]+j])]=-100
                    new_prob = prob_trellis[l][j-1] + transition[l][k] + emission[(UNIVERSAL_TAGS[k],pos_data[sent_inds[i]+j])]
                    if new_prob > max_prob:
                        max_prob = new_prob
                        max_tag =  UNIVERSAL_TAGS[l]
                prob_trellis[k][j] = max_prob
                path_trellis[k][j] = path_trellis[k][j-1]
                path_trellis[k][j].append(max_tag) 
        
        max_tags = list()
        
        for index in prob_trellis.argmax(axis=0):
            max_tags.append(UNIVERSAL_TAGS[index])
        

        for j in range(len(max_tags)):
            results.append(max_tags[j])       
    write_results(test_file_name+'.pred', results)
    
    
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:],"d:t:")
    trainfile = None
    testfile = None
    for opt, arg in opts:
        if opt == "-d":
            trainfile = arg
        elif opt == "-t":
            testfile = arg
        
    tag(trainfile,testfile)