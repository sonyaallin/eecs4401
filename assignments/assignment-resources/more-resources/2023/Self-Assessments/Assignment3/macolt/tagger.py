# The tagger.py starter code for CSC384 A4.

import os
import sys

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

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    
    ntags = len(UNIVERSAL_TAGS)

    # Calculating prior:
    prior = np.zeros(ntags)
    for i in sent_inds:
        prior[UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
    prior = prior/sum(prior)
    prior = np.log(prior)

    #Calculating transition:
    transition = np.zeros((ntags,ntags))
    for i in range(1,len(pos_data)):
        if i not in sent_inds:
            transition[UNIVERSAL_TAGS.index(pos_data[i-1][1]), UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
    transition = transition/(np.sum(transition, axis=1)[:,np.newaxis])
    transition = np.log(transition)

    # Calculating Emissions
    tagOccur = np.zeros(ntags)
    emission = {}
    for i in pos_data:
        if (i[1],i[0]) in emission:
            emission[(i[1],i[0])] += 1
        else:
            emission[(i[1],i[0])] = 1
        tagOccur[UNIVERSAL_TAGS.index(i[1])] += 1
    for i in emission:
        emission[i] = np.log(emission[i]/tagOccur[UNIVERSAL_TAGS.index(i[0])])
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

    # Note* no emission will be treated as p = 0.00001
    s = len(UNIVERSAL_TAGS)
    o = len(pos_data)
    prob = np.zeros((s,o))
    path = [[ None for _ in range(o)] for _ in range(s)]
    for i in range(o):
        # Restarting path for each sentance using prior
        if i in sent_inds:
            for t in range(s):
                em = np.log(0.00001)
                if (UNIVERSAL_TAGS[t],pos_data[i]) in emission:
                    em = emission[(UNIVERSAL_TAGS[t],pos_data[i])]
                prob[t,i] = prior[t]+em
                path[t][i] = [UNIVERSAL_TAGS[t]]
        # Finding probabilities for next stage
        else:
            for t in range(s):
                em = np.log(0.00001)
                if (UNIVERSAL_TAGS[t],pos_data[i]) in emission:
                    em = emission[(UNIVERSAL_TAGS[t],pos_data[i])]
                maxp = np.NINF
                maxs = 0
                for x in range(s): 
                    c = prob[x, i-1]+transition[x,t]+em
                    if c > maxp:
                        maxp = c
                        maxs = x
                prob[t,i] = prob[maxs,i-1]+transition[maxs,t]+em
                path[t][i] = path[maxs][i-1]+[UNIVERSAL_TAGS[t]]
    # Compiling results from paths
    # Gets max probability path from stages 1 iteration
    # before each sentance start (or end of each sentance)
    results = []
    for i in range(1,len(sent_inds)):
        end = sent_inds[i]-1
        temp = []
        maxp = np.NINF
        for t in range(s):
            if prob[t,end] > maxp:
                maxp = prob[t,end]
                temp = path[t][end]
        results = results+temp
    temp = []
    maxp = np.NINF
    # Add final sentance path to result as there is no
    # sentance start index after it. 
    for t in range(s):
        if prob[t,end] > maxp:
            maxp = prob[t,o-1]
            temp = path[t][o-1]
    results = results+temp
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
