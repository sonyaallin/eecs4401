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
    # add end of data to sent_inds
    length = len(pos_data)
    sent_inds.append(length)

    prior = []
    # stores the number of times a tag appears at the beginning of the sentence
    prior_count = [0] * N_tags
    transition = []
    # stores the number of transitions from tag1 to tag2
    transition_count = [[0] * N_tags for i in range(N_tags)]

    # stores the number of transitions for each tag
    tag_count_transitions = [0] * N_tags

    # stores the number of times each tag appears in the data
    tag_count = [0] * N_tags

    # stores the appearance count of each word and its corresponding tag
    word_count = {}
    emission = {}

    # used to get the index of a tag in Universal_Tags
    tag_indices = {}
    for i in range(N_tags):
        tag_indices[UNIVERSAL_TAGS[i]] = i

    # line counter
    index = 0

    # sentence counter
    curr_sentence = 0

    # total number of sentences
    sentences = len(sent_inds) - 1

    # loop through each line of the training data
    for word in pos_data:
        # prior (beginning of sentence)
        if index == sent_inds[curr_sentence]:
            curr_sentence += 1
            prior_count[tag_indices[word[1]]] += 1

        # transition
        if index < sent_inds[curr_sentence] - 1:
            tag_count_transitions[tag_indices[word[1]]] += 1
            next_word = pos_data[index + 1]
            transition_count[tag_indices[word[1]]][
                tag_indices[next_word[1]]] += 1

        # emission
        tag_count[tag_indices[word[1]]] += 1
        entry = (word[1], word[0])
        if entry in word_count:
            word_count[entry] += 1
        else:
            word_count[entry] = 1
        index += 1

    # calculate probabilities given the counts of words and transitions
    for i in range(N_tags):
        prior.append(np.log(prior_count[i] / sentences))
        temp = []
        for j in range(N_tags):
            if transition_count[i][j] == 0:
                temp.append(-np.inf)
            else:
                p = transition_count[i][j] / tag_count_transitions[i]
                temp.append(np.log(p))
        transition.append(temp)

    # calculate the emission probabilities
    for x in word_count:
        emission[x] = np.log(word_count[x]/tag_count[tag_indices[x[0]]])

    prior = np.array(prior)
    transition = np.array(transition)
    return prior, transition, emission


def viterbi(data, prior, transition, emission):
    zero_prob = np.log(1e-5)
    seq = len(data)

    # create the two matrices
    prob_trellis = [[0] * seq for i in range(N_tags)]
    path_trellis = [[[]] * seq for i in range(N_tags)]

    # set initial probabilities
    for i in range(N_tags):
        prob_trellis[i][0] = prior[i] + emission.get((UNIVERSAL_TAGS[i], data[0]), zero_prob)
        path_trellis[i][0] = [UNIVERSAL_TAGS[i]]

    # calculate most probable path to each state for each tag
    for i in range(1, seq):
        for j in range(N_tags):
            l = []
            for x in range(N_tags):
                a = prob_trellis[x][i-1]
                b = transition[x][j]
                c = emission.get((UNIVERSAL_TAGS[j], data[i]), zero_prob)
                # add probabilities since we are using log probabilities
                l.append((a+b+c, x))

            x = max(l)
            prob_trellis[j][i] = x[0]
            path_trellis[j][i] = path_trellis[x[1]][i-1] + [UNIVERSAL_TAGS[j]]

    return prob_trellis, path_trellis


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
    length = len(pos_data)
    sent_inds.append(length)
    results = []

    # run viterbi algorithm for each sentence
    for i in range(1, len(sent_inds)):
        start = sent_inds[i-1]
        end = sent_inds[i]
        data = pos_data[start:end]
        prob_trellis, path_trellis = viterbi(data, prior, transition, emission)

        max_val = -np.inf
        seq = []
        # calculate the most probable path for each sentence and add to results
        for s in range(N_tags):
            if prob_trellis[s][-1] > max_val:
                max_val = prob_trellis[s][-1]
                seq = path_trellis[s][-1]

        results += seq
    write_results(test_file_name + '.pred', results)


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
