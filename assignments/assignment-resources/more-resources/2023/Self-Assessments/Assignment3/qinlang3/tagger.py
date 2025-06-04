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
        
def find_tag_helper(tag):
    for i in range(len(UNIVERSAL_TAGS)):
        if UNIVERSAL_TAGS[i] == tag:
            return i
    

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
    prior = [0 for i in range(len(UNIVERSAL_TAGS))]
    for idx in sent_inds:
        tag = pos_data[idx][1]
        prior[find_tag_helper(tag)] += 1
    prior = np.log(np.array(prior)/len(sent_inds))
    transition = np.zeros((len(UNIVERSAL_TAGS), len(UNIVERSAL_TAGS)))
    cnt = Counter()
    for tag in UNIVERSAL_TAGS:
        cnt[tag] = 0
    for i in range(len(sent_inds)):
        idx = sent_inds[i]
        if i == len(sent_inds)-1:
            idx_after = len(pos_data)
        else:  
            idx_after = sent_inds[i+1]
        for j in range(idx, idx_after-1):
            prev = pos_data[j][1]
            cnt[prev] += 1
            after = pos_data[j+1][1]
            transition[find_tag_helper(prev), find_tag_helper(after)] += 1
    for i in range(len(UNIVERSAL_TAGS)):
        with np.errstate(divide = 'ignore'):
            transition[i,:] = np.log(transition[i,:]/cnt[UNIVERSAL_TAGS[i]])
    emission = {}
    cnt = Counter()
    for tag in UNIVERSAL_TAGS:
        cnt[tag] = 0
    for pair in pos_data:
        cnt[pair[1]] += 1
        if (pair[1], pair[0]) not in emission:
            emission[(pair[1], pair[0])] = 1
        else:
            emission[(pair[1], pair[0])] += 1
    for pair in emission:
        emission[pair] = np.log(emission[pair]/cnt[pair[0]])
    
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
    for i in range(len(sent_inds)):
        # Perform Viterbi algorithm for each sentence.
        idx = sent_inds[i]
        if i == len(sent_inds)-1:
            idx_after = len(pos_data)
        else:  
            idx_after = sent_inds[i+1]
        prob_trellis = np.zeros((len(UNIVERSAL_TAGS), idx_after-idx))
        path_trellis = np.empty((len(UNIVERSAL_TAGS), idx_after-idx), dtype=object)
        for j, tag in enumerate(UNIVERSAL_TAGS):
            if (tag, pos_data[idx]) in emission:          
                prob_trellis[j, 0] = prior[j]*emission[(tag, pos_data[idx])]
            else:
                prob_trellis[j, 0] = prior[j]*np.log(0.00001)
            path_trellis[j, 0] = [tag]
        for j in range(1, idx_after-idx):
            for k, tag in enumerate(UNIVERSAL_TAGS):
                if (tag, pos_data[j+idx]) in emission:
                    x = np.argmin(prob_trellis[:,j-1]*transition[:,k]*emission[(tag, pos_data[j+idx])])
                    prob_trellis[k, j] = prob_trellis[x, j-1]*transition[x,k]*emission[(tag, pos_data[j+idx])]
                else:
                    x = np.argmin(prob_trellis[:,j-1]*transition[:,k]*np.log(0.00001))
                    prob_trellis[k, j] = prob_trellis[x, j-1]*transition[x,k]*np.log(0.00001)
                path_trellis[k, j] = list(path_trellis[x, j-1])
                path_trellis[k, j].append(tag)
        y = np.argmin(prob_trellis[:,idx_after-idx-1])
        results += path_trellis[y,idx_after-idx-1]


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