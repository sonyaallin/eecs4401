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
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning 
                            of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the 
                            i'th tag in UNIVERSAL_TAGS
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
    words = [pos_data[i][1] for i in sent_inds]
    prior = [np.log(words.count(x) / len(sent_inds)) for x in  UNIVERSAL_TAGS]

    count = [[0 for i in range(N_tags)] for i in range(N_tags)]
    transition = [[0 for i in range(N_tags)] for i in range(N_tags)]

    # for i in range(len(pos_data)-1):
    #     now = pos_data[i][1]
    #     next = pos_data[i+1][1]

    #     transition[UNIVERSAL_TAGS.index(now)][UNIVERSAL_TAGS.index(next)] += 1

    # for x in transition:
    #     for i in range(N_tags):
    #         x[i] = np.log(x[i]/)

    tcounter = Counter(x[1] for x in pos_data[:-1])
    for i in range(len(pos_data)-1):
        now = pos_data[i][1]
        next = pos_data[i+1][1]
        if i+1 in sent_inds:
            tcounter[now] -= 1
        else:
            count[UNIVERSAL_TAGS.index(now)][UNIVERSAL_TAGS.index(next)] += 1
    for i in range(N_tags):
        for j in range(N_tags):
            transition[i][j] = np.log(count[i][j] / tcounter[UNIVERSAL_TAGS[i]])

    # for a in range(N_tags):
    #     for b in range(N_tags):
    #         if prior[b] > 0:
    #             transition[a].append(np.log((prior[a] * prior[b])/ prior[b]))
    #         else:
    #             transition[a].append(np.log(10 ** -5))

    # prior = [np.log(x) if x > 0 else np.log(10 **-5) for x in prior]

    emission = {}
    wcounter = Counter(pos_data)
    tcounter = Counter(x[1] for x in pos_data)

    for word, t in pos_data:
        if (t, word) in emission:
            continue
        else:
            emission[(t, word)] = np.log(wcounter[(word, t)] / tcounter[t])

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
    # everything = [[0 for i in range(N_tags)] for x in range(len(pos_data))]
    # results = []

    # for i in range(len(pos_data)):
    #     for j in range(N_tags):
    #         if i == 0:
    #             if (UNIVERSAL_TAGS[j], pos_data[i]) in emission:
    #                 everything[i][j] = prior[j] + emission[(UNIVERSAL_TAGS[j], pos_data[i])]
    #             else:
    #                 everything[i][j] = prior[j]
    #         else:
    #             m = [everything[i-1][x] + transition[x][j] for x in range(N_tags)]
    #             if (UNIVERSAL_TAGS[j], pos_data[i]) in emission:
    #                 everything[i][j] = max(m) + emission[(UNIVERSAL_TAGS[j], pos_data[i])]
    #             else:
    #                 everything[i][j] = max(m)

    # for l in everything:
    #     results.append(UNIVERSAL_TAGS[l.index(max(l))])
    prob = [[0 for i in range(N_tags)] for x in range(len(pos_data))]
    path = [[0 for i in range(N_tags)] for x in range(len(pos_data))]
    for i in range(len(pos_data)):
        for j in range(N_tags):
            if i == 0:
                if (UNIVERSAL_TAGS[j], pos_data[i]) in emission:
                    prob[i][j] = prior[j] + emission[(UNIVERSAL_TAGS[j], pos_data[i])]
                else:
                    # prob[i][j] = prior[j]
                    prob[i][j] = float("-inf")
                path[i][j] = [UNIVERSAL_TAGS[j]]
            else:
                m = [prob[i-1][x] + transition[x][j] for x in range(N_tags)]
                if (UNIVERSAL_TAGS[j], pos_data[i]) in emission:
                    prob[i][j] = max(m) + emission[(UNIVERSAL_TAGS[j], pos_data[i])]
                else:
                    # prob[i][j] = max(m)
                    prob[i][j] = float("-inf")
                temp = path[i-1][m.index(max(m))].copy()
                temp.append(UNIVERSAL_TAGS[j])
                path[i][j] = temp

    print(prob[0])
    print(max(prob[0]))
    results = path[-1][prob[-1].index(max(prob[-1]))]
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