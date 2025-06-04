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
    return [tuple(line.split(' : ')) for line in
            open(path, 'r').read().split('\n')[:-1]]


def read_data_test(path):
    return open(path, 'r').read().split('\n')[:-1]


def read_data_ind(path):
    return [int(line) for line in open(path, 'r').read().split('\n')[:-1]]


def write_results(path, results):
    with open(path, 'w') as f:
        f.write('\n'.join(results))


def read_data_tags(path):
    return [tuple(line.split(' : ')) for line in
            open(path, 'r').read().split('\n')[:-1]]


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

    pos_data = read_data_train(train_file_name + '.txt')
    sent_inds = read_data_ind(train_file_name + '.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    prior = np.zeros(N_tags)
    total = len(sent_inds)
    for i in sent_inds:
        prior[UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
    for i in range(N_tags):
        prior[i] = np.log(prior[i] / total)

    transition = np.zeros((N_tags, N_tags))
    counts = [0] * N_tags
    # for i in range(len(pos_data)):
    #     counts[UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
    curr = 0
    for start_i in sent_inds[1:] + [len(pos_data)]:
        for index in range(curr, start_i - 1):
            i = UNIVERSAL_TAGS.index(pos_data[index][1])
            counts[i] += 1
            j = UNIVERSAL_TAGS.index(pos_data[index + 1][1])
            transition[i][j] += 1
        curr = start_i
    for i in range(N_tags):
        for j in range(N_tags):
            p = transition[i][j] / counts[i]
            if p <= 0:
                transition[i][j] = - np.inf
            else:
                transition[i][j] = np.log(p)

    counts = [0] * N_tags
    for word in pos_data:
        counts[UNIVERSAL_TAGS.index(word[1])] += 1
    emission = {}
    pairs = Counter(pos_data)
    for key in pairs:
        emission[key[1], key[0]] = pairs[key] / counts[
            UNIVERSAL_TAGS.index(key[1])]
        if emission[key[1], key[0]] == 0:
            emission[key[1], key[0]] = - np.inf
        else:
            emission[key[1], key[0]] = np.log(emission[key[1], key[0]])
    return prior, transition, emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name + '.txt')
    sent_inds = read_data_ind(test_file_name + '.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    results = []
    sentences = in_sentence(pos_data, sent_inds)
    for sent in sentences:
        prob_trellis, path_trellis = viterbi(sent, prior, transition, emission)
        m = max_prob(prob_trellis)
        results.extend(path_trellis[m, -1].split(" "))
    write_results(test_file_name+'.pred', results)


def viterbi(data, prior, transition, emission):
    prob_trellis = np.zeros((N_tags, len(data)), np.float)
    path_trellis = np.array([[None] * len(data)] * N_tags)
    for s in range(N_tags):
        try:
            prob_trellis[s, 0] = prior[s] + emission[UNIVERSAL_TAGS[s], data[0]]
        except:
            prob_trellis[s, 0] = prior[s] + np.log(0.0000001)
        path_trellis[s][0] = UNIVERSAL_TAGS[s]

    for word_i in range(1, len(data)):
        for curr_tag in range(N_tags):
            m, v = 0, -np.inf
            for prev_tag in range(N_tags):
                try:
                    e = emission[UNIVERSAL_TAGS[curr_tag], data[word_i]]
                except:
                    e = np.log(0.000001)
                p = prob_trellis[prev_tag, word_i - 1]
                t = transition[prev_tag, curr_tag]
                x = p + t + e
                if x > v:
                    m, v = prev_tag, x
            prob_trellis[curr_tag, word_i] = v
            path_trellis[curr_tag, word_i] = path_trellis[m, word_i - 1] + " " + UNIVERSAL_TAGS[curr_tag]
    return prob_trellis, path_trellis


def max_prob(prob_trellis):
    m, v = 0, - np.inf
    for row in range(N_tags):
        if prob_trellis[row, -1] > v:
            m, v = row, prob_trellis[row, -1]
    return m


def in_sentence(pos_data, sent_inds):
    sentences= []
    curr = 0
    for start_i in sent_inds[1:] + [len(pos_data)]:
        sentences.append(pos_data[curr:start_i])
        curr = start_i
    return sentences


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d") + 1]
    test_file_name = parameters[parameters.index("-t") + 1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
