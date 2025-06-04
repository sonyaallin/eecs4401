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

    start_tags = []
    tags = []
    # 2d matrix of the number of times each tag pair appears
    tag_matrix = np.zeros((len(UNIVERSAL_TAGS), len(UNIVERSAL_TAGS)))
    emission = {}
    prior = []
    # 2d matrix of the probabilities of each tag pair appearing
    transition = np.zeros((len(UNIVERSAL_TAGS), len(UNIVERSAL_TAGS)))
    # calculates the prior probability of each tag
    for index in sent_inds:
        start_tags.append(pos_data[index][1])
    start_count = Counter(start_tags)
    for tag in UNIVERSAL_TAGS:
        prior.append(np.log(start_count[tag] / len(sent_inds)))

    # tag_counts is the number of times each tag occurs
    for item in pos_data:
        tags.append(item[1])
    tag_counts = Counter(tags)

    # calculates the transition counts of all sentences except the last one
    for i in range(len(sent_inds) - 1):
        start = sent_inds[i]
        stop = sent_inds[i + 1] - 1
        while (start < stop):
            tag1 = pos_data[start][1]
            tag2 = pos_data[start + 1][1]
            index1 = UNIVERSAL_TAGS.index(tag1)
            index2 = UNIVERSAL_TAGS.index(tag2)
            tag_matrix[index1][index2] += 1
            start += 1

    # calculates the transition count of the last sentence
    start = sent_inds[len(sent_inds) - 1]
    stop = len(pos_data) - 1
    while(start < stop):
        tag1 = pos_data[start][1]
        tag2 = pos_data[start + 1][1]
        index1 = UNIVERSAL_TAGS.index(tag1)
        index2 = UNIVERSAL_TAGS.index(tag2)
        tag_matrix[index1][index2] += 1
        start += 1

    # caculates the count of times the denominator tag appears for the transition
    denominators = []
    for i in range(len(tag_matrix)):
        denominators.append(0)
        for j in range(len(tag_matrix[i])):
            denominators[i] += tag_matrix[i][j]

    # calculates the transition probabilities for each tag pair
    for i in range(len(tag_matrix)):
        for j in range(len(tag_matrix[i])):
            transition[i][j] = np.log(tag_matrix[i][j] / denominators[i])

    # calculates the emission probabilities
    counts = Counter(pos_data)
    for key in counts:
        word = key[0]
        tag = key[1]
        emission[(tag, word)] = np.log(counts[key] / tag_counts[key[1]])

    return np.array(prior), transition, emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    prob_trellis = np.zeros((len(UNIVERSAL_TAGS), len(pos_data)))
    results = []

    for i in range(len(sent_inds)):
        max, element = float('-inf'), ""
        for state in range(len(UNIVERSAL_TAGS)):
            index = sent_inds[i]
            if (UNIVERSAL_TAGS[state], pos_data[index]) not in emission:
                prob_trellis[state][index] = prior[state] * 0.00001
            else:
                prob_trellis[state][index] = prior[state] * emission[(UNIVERSAL_TAGS[state], pos_data[index])]
            if prob_trellis[state][index] > max:
                max = prob_trellis[state][index]
                element = UNIVERSAL_TAGS[state]
        results.append(element)

        start = sent_inds[i] + 1
        if i == len(sent_inds) - 1:
            stop = len(pos_data)
        else:
            stop = sent_inds[i + 1]
        while(start < stop):
            max, element = float('-inf'), ""
            for state in range(len(UNIVERSAL_TAGS)):
                previous = get_previous_max(prob_trellis, transition, emission, start, state, pos_data)
                if (UNIVERSAL_TAGS[state], pos_data[start]) not in emission and transition[previous, state] == float('-inf'):
                    prob_trellis[state][start] = (prob_trellis[previous][start - 1] * 0.00001 * 0.00001)
                elif (UNIVERSAL_TAGS[state], pos_data[start]) not in emission:
                    prob_trellis[state][start] = (prob_trellis[previous][start - 1] * transition[previous, state] * 0.00001)
                elif transition[previous, state] == float('-inf'):
                    prob_trellis[state][start] = (prob_trellis[previous][start - 1] * 0.00001 *
                    emission[(UNIVERSAL_TAGS[state], pos_data[start])])
                else:
                    prob_trellis[state][start] = (prob_trellis[previous][start - 1] * transition[previous, state] *
                    emission[(UNIVERSAL_TAGS[state], pos_data[start])])
                if prob_trellis[state][start] > max:
                    max = prob_trellis[state][start]
                    element = UNIVERSAL_TAGS[state]
            start += 1
            results.append(element)

    write_results(test_file_name+'.pred', results)


def get_previous_max(prob_trellis, transition, emission, current_word, current_state, pos_data):
    """
    Returns the state which has the maximum probability of reaching at the given state
    """
    previous = 0
    max = float('-inf')
    value = 0
    for s in range(len(UNIVERSAL_TAGS)):
        if (((UNIVERSAL_TAGS[current_state], pos_data[current_word]) not in emission) and
            (transition[s, current_state] == float('-inf'))):
            value = (prob_trellis[s][current_word - 1] * 0.00001 * 0.00001)
        elif (UNIVERSAL_TAGS[current_state], pos_data[current_word]) not in emission:
           value = (prob_trellis[s][current_word - 1] * transition[s, current_state] * 0.00001)
        elif transition[s, current_state] == float('-inf'):
            value = (prob_trellis[s][current_word - 1] * 0.00001 *
            emission[(UNIVERSAL_TAGS[current_state], pos_data[current_word])])
        else:
            value = (prob_trellis[s][current_word - 1] * transition[s, current_state] *
            emission[(UNIVERSAL_TAGS[current_state], pos_data[current_word])])
        if value > max:
            max = value
            previous = s
    return previous


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
