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

    prior = np.zeros(N_tags)
    transition = np.zeros((N_tags,N_tags))
    emission = {}
    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    tags = {UNIVERSAL_TAGS[i]:i for i in range(N_tags)}
    tcount = np.zeros(N_tags)

    n = len(sent_inds)
    k=0
    for i in range(n):
        prior[tags[pos_data[sent_inds[i]][1]]] += 1
        if i <n-1:
            for j in range(sent_inds[i], sent_inds[i+1]-1):
                transition[tags[pos_data[j][1]],tags[pos_data[j+1][1]]] += 1
        else:
            for j in range(sent_inds[i], len(pos_data)-1):
                transition[tags[pos_data[j][1]],tags[pos_data[j+1][1]]] += 1
    for w in pos_data:
        k+=1
        tcount[tags[w[1]]]+=1
        if (w[1],w[0]) in emission:
            emission[(w[1],w[0])]+=1
        else:
            emission[(w[1],w[0])] =1
    
    tcount = np.log(tcount/np.sum(tcount)) + np.log(len(pos_data))
    for w in emission:
        emission[w] = np.log(emission[w]) - tcount[tags[w[0]]] 
    
    
    return np.log(prior/np.sum(prior)), np.log(transition)-np.log(np.reshape(np.sum(transition,1),(N_tags,1))), emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    tags = {i:UNIVERSAL_TAGS[i] for i in range(N_tags)}

    results = []
    prob = np.zeros(N_tags)


    for i in range(len(sent_inds)):
        if i <len(sent_inds)-1:
            n = sent_inds[i+1]
        else:
            n = len(pos_data)
        

        for j in range(N_tags):
            if (tags[j],pos_data[sent_inds[i]]) not in emission:
                prob[j] = -10000
            else:
                prob[j] = emission[(tags[j],pos_data[sent_inds[i]])]
        prob += prior


        results.append(tags[np.argmax(prob)])
        for j in range(sent_inds[i]+1, n):
            prob = np.tile(np.reshape(prob,(N_tags,1)),(1,N_tags))
            prob += transition
            for k in range(N_tags):
                if (tags[k],pos_data[j]) not in emission:
                    prob[:,k] -= 10000
                else:
                    prob[:,k] += emission[(tags[k],pos_data[j])]
            c = np.max(prob)
            prob = np.log(np.sum(np.exp(prob-c),0)) +c
            results.append(tags[np.argmax(prob)])
    
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
    tag(train_file_name, test_file_name)