# The tagger.py starter code for CSC384 A4.

import os
import sys
from tkinter import N

import numpy as np
from collections import Counter

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


  


    #Prior
    prior = [0 for x in UNIVERSAL_TAGS]

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    for i in sent_inds:
        prior[UNIVERSAL_TAGS.index(pos_data[i][1])] += 1

    prior = np.divide(prior,len(sent_inds))

    prior = np.log(prior)


    

    #Transition 
    transition = np.zeros(shape=(N_tags, N_tags))
    prev = ''
    for i in range(len(pos_data)):
        if i in sent_inds:
            prev = pos_data[i][1]
        else:
            transition[UNIVERSAL_TAGS.index(prev)][UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
            prev = pos_data[i][1]

    transition = np.divide(transition,np.sum(transition,axis=1)[:,None])
    transition = np.log(transition)

     #Em
    d = {}
    s = {}
    emission = {}

    for x in range(0,len(pos_data)):
        if (pos_data[x][1],pos_data[x][0]) in d.keys():
            d[(pos_data[x][1],pos_data[x][0])] += 1
        else:
            d[(pos_data[x][1],pos_data[x][0])] = 1
        s[pos_data[x][1]] = s.get(pos_data[x][1], 0) + 1

    # emission

    for i in d.keys():
        d[i] = np.log(d[i]/s[i[0]])
    
        
    emission = d


   
    
    ####################
    # STUDENT CODE HERE
    ####################

    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')
    results = []
    prob = []
    path = []

    # for z in range(N_tags):
    #     prob.append([])
    #     path.append([])
    #     for y in range(len(pos_data)):
    #         prob[z].append([])
    #         # path[z].append([])

    prob = np.zeros(shape=(N_tags, len(pos_data)))
    # path = np.zeros(shape=(N_tags, len(pos_data)))

    temp_1 = []
    for i in range(N_tags):
        prob[i][0] = prior[i] * emission.get((UNIVERSAL_TAGS[i],pos_data[0]), 0.00001)
        temp_1.append(prob[i][0])
        # path[i][0] = [UNIVERSAL_TAGS[i]]

    results.append(UNIVERSAL_TAGS[np.argmax(temp_1)])

    for word_i in range(1,len(pos_data)):
        
        prob_temp = []
        for s in range(N_tags):
                
            emm = emission.get((UNIVERSAL_TAGS[s],pos_data[word_i]), 0.00001)
            
            t = []
            for x in range(N_tags):
                t.append(transition[x][s] * emm)
            x = np.argmax(t)

            prob[s][word_i] =  transition[x][s] * emm
            # path[s][word_i] = path[x][word_i-1] + [(UNIVERSAL_TAGS[s])]
            prob_temp.append(prob[s][word_i])
        p = np.argmax(prob_temp)

        results.append(UNIVERSAL_TAGS[p])
    

    ####################
    # STUDENT CODE HERE
    ####################

    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag (train_file_name, test_file_name)