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
    tags = len(UNIVERSAL_TAGS)
    prior = np.zeros(len(UNIVERSAL_TAGS)) + 1e-5
    transition = np.zeros((tags, tags)) # + 1e-16
    emission = {}
    tag_counts = np.zeros(tags)
    tag_counts2 = np.zeros(tags)
    
    # Calculate prior
    for ind in sent_inds:
        prior[UNIVERSAL_TAGS.index(pos_data[ind][1])] += 1

    prior = np.log(prior/np.sum(prior))

    # Calculate transition
    sentences = [pos_data[sent_inds[i]:sent_inds[i+1]] for i in range(len(sent_inds)-1)]
    sentences.append(pos_data[sent_inds[-1]:])

    for s in sentences:
        for i in range(len(s) - 1):
            tag_i = s[i][1]
            tag_j = s[i+1][1]
            tag_counts[UNIVERSAL_TAGS.index(tag_i)] += 1
            transition[UNIVERSAL_TAGS.index(tag_i)][UNIVERSAL_TAGS.index(tag_j)] += 1

    
    for i in range(0,tags):
        transition[i] = np.log(transition[i]/tag_counts[i])
    
    # Calculate emission
    for pair in pos_data:
        word = pair[0]
        tag = pair[1]
        if (tag, word) not in emission:
            emission[(tag, word)] = 1
        else:
            emission[(tag, word)] += 1
        tag_counts2[UNIVERSAL_TAGS.index(tag)] += 1

    for key in emission:
        emission[key] = np.log(emission[key]/tag_counts2[UNIVERSAL_TAGS.index(key[0])])

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
    tags = len(UNIVERSAL_TAGS)
    results = []
    transition[np.isinf(transition)] = -1e-5

    
    prior = np.power(np.e, prior)
    transition = np.power(np.e, transition)
    for key in emission:
        emission[key] = np.e ** emission[key]

    # For each sentence, find the most likely path
    for i in range(len(sent_inds)):
        start = sent_inds[i]
        if i == len(sent_inds) - 1:
            sentence = pos_data[start:]
        else:
            end = sent_inds[i+1]
            sentence = pos_data[start:end]

        prob_trellis = np.zeros((tags, len(sentence)))
        path_trellis = [['' for i in range(len(sentence))] for j in range(tags)]
        
        # Find initial probabilities
        for t_i in range(tags):
            if (UNIVERSAL_TAGS[t_i], sentence[0]) not in emission:
                prob_trellis[t_i][0] = prior[np.argmax(prior)] * 1e-5
                path_trellis[t_i][0] = UNIVERSAL_TAGS[np.argmax(prior)]
            else:
                prob_trellis[t_i][0] = prior[t_i] * emission[(UNIVERSAL_TAGS[t_i], sentence[0])]
                path_trellis[t_i][0] = UNIVERSAL_TAGS[t_i]

        # Find probability of each X2-Xn given previous Trellis probability
        for s_i in range(1, len(sentence)):
            for t_i in range(tags):
                tag = UNIVERSAL_TAGS[t_i]
                word = sentence[s_i]
                if (tag, word) in emission:
                    x = np.argmax(prob_trellis[:, s_i-1] * transition[:, t_i] * emission[(tag, word)])
                    prob_trellis[t_i][s_i] = prob_trellis[x][s_i-1] * transition[x][t_i] * emission[(tag, word)]
                    path_trellis[t_i][s_i] = path_trellis[x][s_i-1] + ',' + tag
                else:
                    x = np.argmax(prob_trellis[:, s_i-1] * transition[:, t_i] * 1e-5) 
                    prob_trellis[t_i][s_i] = prob_trellis[x][s_i-1] * transition[x][t_i] * 1e-5
                    path_trellis[t_i][s_i] = path_trellis[x][s_i-1] + (',' + tag)

        results += (np.asarray(path_trellis)[np.argmax(prob_trellis[:, -1]), -1].split(','))

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