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

    prior = []
    transition = np.zeros((N_tags, N_tags))
    emission = {}

    cntr = None # multi-purpose Counter

    # Getting prior done
    prior_tags = [pos_data[int(l)] for l in sent_inds]
    cntr = Counter([t[1] for t in prior_tags])

    for t in UNIVERSAL_TAGS:
        prior = np.append(prior, [np.log(cntr.get(t)/len(prior_tags))])

    # Getting transition done         
    sentences = []
    pos = 0
    for i in range(1, len(sent_inds)):
        sentences.append(pos_data[pos:sent_inds[i]])
        pos = sent_inds[i]
    sentences.append(pos_data[sent_inds[-1]:])

    for s in sentences:
        for s1, s2 in zip(s, s[1:]):
            i = UNIVERSAL_TAGS.index(s1[1])
            j = UNIVERSAL_TAGS.index(s2[1])
            transition[i][j] += 1

    for c, r in enumerate(transition):
        transition[c] = [np.log(float(i)/sum(r)) for i in r]

    transition = np.asarray(transition)

    # Getting emission done
    tag_sequence = [l[1] for l in pos_data]
    tag_cntr = Counter(tag_sequence)
    cntr = Counter(pos_data)

    for k, v in cntr.items():
        if v != 0:
            emission[(k[1], k[0])] = np.log(v/tag_cntr.get(k[1]))

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
    results = []

    sentences = []
    pos = 0
    for i in range(1, len(sent_inds)):
        sentences.append(pos_data[pos:sent_inds[i]])
        pos = sent_inds[i]
    sentences.append(pos_data[sent_inds[-1]:])

    for s in sentences:
        prob_trellis = np.zeros((N_tags, len(s)))
        path_trellis = np.zeros((N_tags, len(s))).tolist()

        for t in range(N_tags):
            if emission.get((UNIVERSAL_TAGS[t], s[0])):
                prob_trellis[t, 0] = prior[t] + emission.get((UNIVERSAL_TAGS[t], s[0]))
            else:    # If emission with provided key does not exist - take of a very small probability instead log(0.0000000001)
                prob_trellis[t, 0] = prior[t] + np.log(0.0000000001)

            path_trellis[t][0] = [UNIVERSAL_TAGS[t]]

        for w in range(1, len(s)):
            for t in range(N_tags):
                if emission.get((UNIVERSAL_TAGS[t], s[w])):
                    x = np.argmax([prob_trellis[t1, w - 1] + transition[t1, t] + emission.get((UNIVERSAL_TAGS[t], s[w])) for t1 in range(N_tags)])
                    prob_trellis[t, w] = prob_trellis[x, w - 1] + transition[x, t] + emission.get((UNIVERSAL_TAGS[t], s[w]))
                else:   # If emission with provided key does not exist - take of a very small probability instead log(0.0000000001)
                    x = np.argmax([prob_trellis[t1, w - 1] + transition[t1, t] + np.log(0.0000000001) for t1 in range(N_tags)])
                    prob_trellis[t, w] = prob_trellis[x, w - 1] + transition[x, t] + np.log(0.0000000001)

                path_trellis[t][w] = path_trellis[x][w - 1] + [UNIVERSAL_TAGS[t]]
        
        results += path_trellis[np.argmax(prob_trellis[:, -1])][-1]

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