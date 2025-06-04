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

    # Calculating prior
    tag_total = [0] * len(UNIVERSAL_TAGS)
    prior_total = 0
    prior = []

    for i in sent_inds:
        tag = pos_data[i][1]
        tag_total[UNIVERSAL_TAGS.index(tag)] += 1
        prior_total += 1

    # Calculat log probabilitty
    prior_total = np.log(prior_total)
    for v in tag_total:
        if v == 0:
            prior.append(-np.inf)
        else:
            prior.append(np.log(v) - prior_total)

    # Calculating transition
    transition = [[]] * len(UNIVERSAL_TAGS)
    for i in range(len(transition)):
        transition[i] = [0] * len(UNIVERSAL_TAGS)

    total = 0

    ind = 0
    while ind < len(pos_data):
        while ind in sent_inds:
            ind += 1

        tag_i = pos_data[ind - 1][1]
        tag_j = pos_data[ind][1]

        transition[UNIVERSAL_TAGS.index(tag_i)][UNIVERSAL_TAGS.index(tag_j)] += 1
        tag_total[UNIVERSAL_TAGS.index(tag_j)] += 1
        total += 1

        ind += 1

    # Calculate marginalized log probability of each transition
    total_log = np.log(total)
    i_sums = []
    for vals in transition:
        i_sums.append(sum(vals))
    for i in range(len(transition)):
        for j in range(len(transition[i])):
            if transition[i][j] == 0:
                transition[i][j] = -np.inf
            else:
                transition[i][j] = np.log(transition[i][j]) - np.log(i_sums[i])

    # Calculating emission
    d = Counter(pos_data)

    # Invert key (word | tag)
    emission = Counter()
    for k in d:
        emission[(k[1], k[0])] = d[k]

    # Calulcate conditional log probability of word given tag
    for v in emission:
        tag_ind = UNIVERSAL_TAGS.index(v[0])
        emission[v] = np.log(emission[v]) - np.log(tag_total[tag_ind])

    return np.array(prior), np.array(transition), emission
    

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

    # print(sent_inds)
    # Calculate most probable path for every sentence sequence except the last
    for i in range(len(sent_inds) - 1):
        i_1, i_2 = sent_inds[i], sent_inds[i+1]
        path = viterbi(pos_data[i_1:i_2], UNIVERSAL_TAGS, prior, transition, emission)
        results = results + path

    # The last sequence
    i_1, i_2 = sent_inds[-1], len(pos_data)
    path = viterbi(pos_data[i_1:i_2], UNIVERSAL_TAGS, prior, transition, emission)
    results = results + path

    write_results(test_file_name+'.pred', results)

def viterbi(O, S, init, A, B):
    # Initialize matrices
    prob_trellis = []
    path_trellis = []

    for i in range(len(S)):
        prob_trellis.append([])
        path_trellis.append([])
        for j in range(len(O)):
            prob_trellis[i].append(-np.inf)
            path_trellis[i].append([])

    # Determine trellis values for X1
    for s in range(len(S)):
        # Add a very small emission value if we don't know what it is or if it doesn't exist
        if B[(S[s], O[0])] == 0:
            prob_trellis[s][0] = init[s] + np.log(0.000001)
        else:
            prob_trellis[s][0] = init[s] + B[(S[s], O[0])] 
        path_trellis[s][0] = [S[s]]

    # For X2-XT find each current state's most likely prior state x.
    for o in range(1, len(O)):
        for s in range(len(S)):
            # Add a very small emission value if we don't know what it is or if it doesn't exist
            if B[(S[s], O[o])] == 0:
                x = np.argmax([prob_trellis[x][o-1] + A[x][s] + np.log(0.000001) for x in range(len(S)) ])
                prob_trellis[s][o] = prob_trellis[x][o-1] + A[x][s] + np.log(0.000001)
            else:
                x = np.argmax([prob_trellis[x][o-1] + A[x][s] + B[(S[s], O[o])] for x in range(len(S)) ])
                prob_trellis[s][o] = prob_trellis[x][o-1] + A[x][s] + B[(S[s],O[o])]

            path_trellis[s][o] = path_trellis[x][o-1].copy() + [S[s]]

    # Best path (highest probability)
    x = np.argmax([prob_trellis[x][-1] for x in range(len(S))])

    return path_trellis[x][-1]

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