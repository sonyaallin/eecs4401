# The tagger.py starter code for CSC384 A4.

import os
import sys
import numpy as np
from collections import Counter
from collections import defaultdict

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
    total = len(sent_inds)
    n = len(UNIVERSAL_TAGS)
    index = dict()
    for i, tg in enumerate(UNIVERSAL_TAGS):         # tag to index dictionary
        index[tg] = i

    prior = [0 for i in range(n)] #count of tag appearing as 1st word in sequence / divided by # of sequences
    transition = [[0 for i in range(n)] for j in range(n)] #count of word i followed by a word j (divided with count later)
    count = defaultdict(int)        #count of word i
    emissionC = defaultdict(int)    #count of (tag, word)
    emissionT = defaultdict(int)    #count of tag

    #Populating the arrays/dicts
    e = sent_inds[0]
    tg = pos_data[e][1]
    prior[index[tg]] += 1/total
    for i in range(1, len(sent_inds)):
        s, e = sent_inds[i-1], sent_inds[i]
        tg = pos_data[e][1]
        prior[index[tg]] += 1/total
        w, tg = pos_data[s]
        key = tg, w
        emissionC[key] += 1
        emissionT[tg] += 1
        for k in range(s+1, e):
            _, prev = pos_data[k-1]
            w, curr = pos_data[k]
            key = curr, w
            emissionC[key] += 1
            emissionT[curr] += 1
            prev, curr = index[prev], index[curr]
            count[prev] += 1
            transition[prev][curr] += 1

    w, tg = pos_data[e]
    key = tg, w
    emissionC[key] += 1
    emissionT[tg] += 1
    for k in range(e+1, len(pos_data)):
        _, prev = pos_data[k-1]
        w, curr = pos_data[k]
        key = curr, w
        emissionC[key] += 1
        emissionT[curr] += 1
        prev, curr = index[prev], index[curr]
        count[prev] += 1
        transition[prev][curr] += 1

    for i in range(n):
        for j in range(n):
            transition[i][j] = transition[i][j] / count.get(i, 1e-10)  #count of word i followed by a word j / count of word i
    emission = dict()
    for key in emissionC:
        tg, _ = key
        emission[key] = np.log(emissionC[key] / emissionT[tg])         #count of (tag, word) / count of tag

    return np.log(prior), np.log(transition), emission


def viterbi(O, S, P, A, B):
    prob_trellis = [[0 for i in range(len(O))] for j in range(len(S))]
    path_trellis = [[[] for i in range(len(O))] for j in range(len(S))]

    for s in range(len(S)):
        prob_trellis[s][0] = P[s] + B.get((S[s], O[0]), np.log(1e-10))
        path_trellis[s][0] = [S[s]]

    for o in range(1, len(O)):
        for s in range(len(S)):
            x = np.argmax([prob_trellis[i][o-1]+A[i][s]+B.get((S[s], O[o]), np.log(1e-10)) for i in range(len(S))])
            prob_trellis[s][o] = prob_trellis[x][o-1]+A[x][s]+B.get((S[s], O[o]), np.log(1e-10))
            path_trellis[s][o] = path_trellis[x][o-1] + [S[s]]

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
    sent_inds.append(len(pos_data))
    for i in range(1, len(sent_inds)):
        s, e = sent_inds[i-1], sent_inds[i]
        O = []
        for k in range(s, e):               #make observations for current sequence
            O.append(pos_data[k])
        prob, path = viterbi(O, UNIVERSAL_TAGS, prior, transition, emission)
        mx, index = float('-inf'), -1
        for j in range(len(UNIVERSAL_TAGS)):  # find best probability
            if prob[j][-1] >= mx:
                mx, index = prob[j][-1], j
        results.extend(path[index][-1])     #add prediction for current sequence
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