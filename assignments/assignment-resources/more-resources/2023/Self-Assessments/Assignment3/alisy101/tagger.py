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
    emission = {}
    tagcount = {} #denominator emission probability. Counts the number of times a tag appears
    ind = {UNIVERSAL_TAGS[i]:i for i in range(len(UNIVERSAL_TAGS))}  #this dictionary maps tags to index according to UNIVERSAL_TAGS
    transitiondc = [[0 for i in range(N_tags)] for i in range (N_tags)]
    prior = [0 for i in range(N_tags)]
    counts = [[0] for i in range(N_tags)]
    pos_i = 0
    sent_i = 0

    for tup in pos_data:
        tagword = (tup[1], tup[0])
        if tagword in emission:
            emission[tagword] += 1
        else:
            emission[tagword] = 1
        if tup[1] in tagcount:  
            tagcount[tup[1]] += 1
        else:
            tagcount[tup[1]] = 1
        if sent_i < len(sent_inds) and sent_inds[sent_i] == pos_i: #if we are looking at the beginning of a sentence
            #so we make prior table
            sent_i += 1
            prior[ind[tup[1]]] += 1/len(sent_inds)
        else:
            transitiondc[ind[pos_data[pos_i-1][1]]][ind[tup[1]]] += 1 #we are not looking at beginning of a sentence
            #so we can make transition table

        try: #edge case since last sentence does not have an index to end.
            if pos_i + 1 != sent_inds[sent_i]:
                counts[ind[tup[1]]][0] += 1
        except:
            if pos_i+1 != len(pos_data):
                counts[ind[tup[1]]][0] += 1
        pos_i+=1

    for tagword in emission:
        emission[tagword] = np.log(emission[tagword]/tagcount.get(tagword[0], 1e-5))
    prior = np.log(prior)
    transition = np.log(np.array(transitiondc)/np.array(counts))
    return prior, transition, emission

def most_likely_prior_state(prob_trellis, A, B, obs, s, word): #helper to get most likely prior state
    currmax = float('-inf')
    ind = -1
    for x in range(len(UNIVERSAL_TAGS)):
        curr = prob_trellis[x][obs] + A[x][s] + B.get((UNIVERSAL_TAGS[s], word), np.log(1e-5))
        if curr >= currmax:
            currmax = curr
            ind = x
    return ind, currmax
def viterbi(pos_data, S, prior, A, B, prob_trellis, path_trellis, tup): #viterbi algorithm from class
    for s in range(len(S)):
        prob_trellis[s][0] = prior[s] + B.get((S[s], pos_data[tup[0]]), np.log(1e-5))
        path_trellis[s][0] = [S[s]]
    for obs in range(1, tup[1] - tup[0]):
        for s in range(len(S)):
            x, mx = most_likely_prior_state(prob_trellis, A, B, obs-1, s, pos_data[tup[0] + obs])
            prob_trellis[s][obs] = mx
            path_trellis[s][obs] = path_trellis[x][obs-1] + [S[s]]
    return prob_trellis, path_trellis

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
    results = []
    for i in range(len(sent_inds)):
        if i+1 >= len(sent_inds):
            prob_trellis = [[0 for z in range(len(pos_data) - sent_inds[i])] for k in range(len(UNIVERSAL_TAGS))] #maybe pos-data - 1
            path_trellis = [[[] for z in range(len(pos_data) - sent_inds[i])] for k in range(len(UNIVERSAL_TAGS))]
            probs, paths = viterbi(pos_data, UNIVERSAL_TAGS, prior, transition, emission, prob_trellis, path_trellis, (sent_inds[i], len(pos_data))) 
        else:
            prob_trellis = [[0 for z in range(sent_inds[i+1] - sent_inds[i])] for k in range(len(UNIVERSAL_TAGS))] 
            path_trellis = [[[] for z in range(sent_inds[i+1] - sent_inds[i])] for k in range(len(UNIVERSAL_TAGS))]
            probs, paths = viterbi(pos_data, UNIVERSAL_TAGS, prior, transition, emission, prob_trellis, path_trellis, (sent_inds[i], sent_inds[i+1]))
            currmax = float('-inf')
            index = -1

        for j in range(len(UNIVERSAL_TAGS)):
            curr = probs[j][-1]
            if curr > currmax:
                currmax = curr
                index = j
        results += paths[index][-1]
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
