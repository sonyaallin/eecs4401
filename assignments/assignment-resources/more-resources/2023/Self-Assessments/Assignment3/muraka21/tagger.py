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

# ------------------------- start of helper functions -------------------------

def compute_prior(word_tag_list, index_list):
    """
    returns the prior log probabilities
    """
    num_total_possibilities = len(index_list)
    sums = np.zeros(N_tags)
    for index in index_list:
        word_tag = word_tag_list[index]
        sums[UNIVERSAL_TAGS.index(word_tag[1])] += 1
    return np.log(sums / num_total_possibilities)

def compute_transition(word_tag_list, index_list):
    """return the transition matrix"""
    matrix = np.zeros([N_tags, N_tags])
    total_tag_transitions = np.zeros(N_tags)
    total_transitions = 0
    # each entry in the total_transitions array will be the total number of
    # transitions from the i-th tag to any other tag
    for i in range(len(word_tag_list) - 1):
        # only update the matrix if the next tag is not the beginning of a new
        # sentence
        if i + 1 not in index_list:
            curr_tag = word_tag_list[i][1]
            next_tag = word_tag_list[i + 1][1]
            index_curr_tag = UNIVERSAL_TAGS.index(curr_tag)
            index_next_tag = UNIVERSAL_TAGS.index(next_tag)
            matrix[index_curr_tag, index_next_tag] += 1
            # my idea is to also compute the total number of transitions for each
            # tag, and then divide the sum that I created in the matrix so that
            # I find the probability of the transitions, I cannot forget to apply
            # the log to them
            total_tag_transitions[index_curr_tag] += 1
        total_transitions += 1
    # all entries in the matrix should be now of the format P(tag_j and tag_i)
    matrix /= total_transitions
    matrix = np.log(matrix)
    # we have to divide the entries by P(tag_i)
    tags_probability = total_tag_transitions / len(word_tag_list)
    tags_probability = np.log(tags_probability)
    for j in range(N_tags):
        matrix[j] = matrix[j] - tags_probability[j]

    return matrix

def compute_emissions(word_tag_list):
    """returns the emission dictionary"""
    emission = {}
    tag_sum = np.zeros(N_tags)
    for word_tag in word_tag_list:
        tag_word = (word_tag[1], word_tag[0])
        emission.setdefault(tag_word, 0)
        emission[tag_word] += 1
        curr_tag = tag_word[0]
        index_curr_tag = UNIVERSAL_TAGS.index(curr_tag)
        tag_sum[index_curr_tag] += 1
    # so I have the sum of (word, tag), and the sum of each tag
    # now I have to divide both values by the length of word_tag_list since
    # it is all the possible events
    num_total_events = len(word_tag_list)
    tag_prob = tag_sum / num_total_events
    for key in emission.keys():
        emission[key] /= num_total_events
        # now I need to divide the values in sum_dict by the values in tag_sum
        # to get the conditional probabilities
        tag = key[0]
        emission[key] /= tag_prob[UNIVERSAL_TAGS.index(tag)]
        # now to finalize do the log probability
        emission[key] = np.log(emission[key])

    return emission


def create_path_list(rows, columns):
    l = []
    for i in range(rows):
        l.append([])
        for j in range(columns):
            l[i].append([])
    return l
# -------------------------- end of helper functions --------------------------

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
    prior = compute_prior(pos_data, sent_inds)
    transition = compute_transition(pos_data, sent_inds)
    emission = compute_emissions(pos_data)
    ####################

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

    # performing the viterbi algorithm
    # setting up the track variables
    prob_trellis = np.zeros([len(UNIVERSAL_TAGS), len(pos_data)])
    path_trellis = create_path_list(len(UNIVERSAL_TAGS), len(pos_data))

    # performing the iterations
    for s in range(len(UNIVERSAL_TAGS)):
        # checking if the tag, word tuple is in the emission dict, if not there
        # is no emission value
        if (UNIVERSAL_TAGS[s], pos_data[0]) in emission:
            prob_trellis[s, 0] = prior[s] + emission[(UNIVERSAL_TAGS[s], pos_data[0])]
        else:
            prob_trellis[s, 0] = prior[s] + np.log(0.00001)
        path_trellis[s][0].append(s)

    for o in range(1, len(pos_data)):
        for s in range(len(UNIVERSAL_TAGS)):
            # checking if the tag, word tuple is in the emission dict
            if (UNIVERSAL_TAGS[s], pos_data[o]) in emission:
                prob_emission = emission[(UNIVERSAL_TAGS[s], pos_data[o])]
            else:
                prob_emission = np.log(0.00001)
            x = np.argmax(prob_trellis[:, o - 1] + transition[:, s] + prob_emission)
            prob_trellis[s, o] = prob_trellis[x, o - 1] + transition[x, s] + prob_emission
            path_trellis[s][o] = [path_trellis[x][o - 1][-1]] + [s]

    # since I set up my trellis to only remember the previous step now I need
    # to traverse back and build the results list with the tags
    results = []
    pair = path_trellis[-1][-1]
    for i in range(1, len(pos_data)):
        previous_index = pair[0]
        results.insert(0, UNIVERSAL_TAGS[pair[1]])
        pair = path_trellis[previous_index][len(pos_data) - 1 - i]
    # adding the first POS to results
    results.insert(0, UNIVERSAL_TAGS[pair[0]])

    ####################
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
