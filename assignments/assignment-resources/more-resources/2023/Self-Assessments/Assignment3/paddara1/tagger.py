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
                            - The (i,j)'th entry stores the log probability of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
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
    prior = np.empty(N_tags, dtype=float)  # prior[i] = log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sentence
    transition = np.empty((N_tags, N_tags), dtype=float)
    emission = dict()  # (str, str) -> float

    # Prior
    num_sentences = len(sent_inds)  # number of sentences in training file
    tag_to_count_1 = dict()  # maps each universal tag to number of occurrences, only considering words that start sentences
    for index in sent_inds:
        tag = pos_data[index][1]
        tag_to_count_1[tag] = tag_to_count_1.get(tag, 0) + 1

    for i, tag in enumerate(UNIVERSAL_TAGS):
        if tag_to_count_1.get(tag, 0) > 0:
            prior[i] = np.log(tag_to_count_1.get(tag) / num_sentences)  # compute log probability
        else:
            prior[i] = float('-inf')

    # Transition
    transitions_to_count = dict()  # maps each transition in train_file_name to its frequency
    for i in range(1, len(sent_inds)):
        # the current sentence starts at sent_inds[i]
        # the previous sentence starts at sent_inds[i-1] and ends at sent_inds[i] - 1
        for j in range(sent_inds[i-1], sent_inds[i] - 1):
            transitions_to_count[(pos_data[j][1], pos_data[j+1][1])] = transitions_to_count.get((pos_data[j][1], pos_data[j+1][1]), 0) + 1

    # the last sentence starts at sent_inds[-1] and ends at pos_data[-1]
    for i in range(sent_inds[-1], len(pos_data) - 1):
        transitions_to_count[(pos_data[i][1], pos_data[i + 1][1])] = transitions_to_count.get((pos_data[i][1], pos_data[i + 1][1]), 0) + 1

    for i, tag1 in enumerate(UNIVERSAL_TAGS):
        curr_sum = 0  # stores the number of occurrences of the current (tag1, tag2) pair where tag1 is constant
        for tag2 in UNIVERSAL_TAGS:
            curr_sum += transitions_to_count.get((tag1, tag2), 0)
        # e.g. on the 1st iteration, curr_sum = # of transitions of the form (VERB -> x) where x is any tag
        # on the 2nd iteration, curr_sum = # of transitions of the form (NOUN -> x) where x is any tag

        for j, tag2 in enumerate(UNIVERSAL_TAGS):
            if transitions_to_count.get((tag1, tag2), 0) > 0 and curr_sum > 0:
                transition[i][j] = np.log(transitions_to_count.get((tag1, tag2)) / curr_sum)
            else:
                transition[i][j] = float('-inf')

    # Emission
    tag_to_count_2 = dict()  # maps each universal tag to number of occurrences, considering all words
    tag_word_to_count = dict()  # maps each (universal tag, word) in pos_data to number of occurrences
    for word, tag in pos_data:
        tag_to_count_2[tag] = tag_to_count_2.get(tag, 0) + 1
        tag_word_to_count[(tag, word)] = tag_word_to_count.get((tag, word), 0) + 1

    for (tag, word), value in tag_word_to_count.items():
        key = (tag, word)
        if tag_word_to_count.get(key, 0) > 0 and tag_to_count_2.get(tag, 0) > 0:
            emission[key] = np.log(tag_word_to_count.get(key) / tag_to_count_2.get(tag))
        else:
            emission[key] = float('-inf')

    return prior, transition, emission


def viterbi(sent_inds, pos_data, prior, transition, emission):
    """
    """
    ans = []
    small_num = 0.0000001
    sentences = []  # List[str]: all sentences
    for i in range(len(sent_inds) - 1):
        # the current sentence starts at index and ends at next_index
        index = sent_inds[i]
        next_index = sent_inds[i+1]
        sentences.append(pos_data[index:next_index])
    sentences.append(pos_data[sent_inds[-1]:])  # last sentence

    for sentence in sentences:
        prob_trellis = np.zeros((N_tags, len(sentence)))
        path_trellis = np.zeros((N_tags, len(sentence)), dtype=object)

        # for the first word
        for s, tag in enumerate(UNIVERSAL_TAGS):
            val = emission.get((tag, sentence[0]), np.log(small_num))
            emission[(tag, sentence[0])] = val
            prob_trellis[s, 0] = prior[s] + val
            path_trellis[s, 0] = [tag]

        # for every word after the first find most likely prior state x
        for o, word in enumerate(sentence[1:], start=1):
            for s, tag in enumerate(UNIVERSAL_TAGS):
                # compute argmax
                lst = np.zeros(N_tags)
                val = emission.get((tag, word), np.log(small_num))
                emission[(tag, sentence[0])] = val
                for i in range(N_tags):
                    curr = prob_trellis[i, o-1] + transition[i, s] + val
                    lst[i] = curr
                x = np.argmax(lst)
                prob_trellis[s, o] = prob_trellis[x, o-1] + transition[x, s] + val
                path_trellis[s, o] = path_trellis[x, o-1] + [tag]

        last_col = prob_trellis[:, -1]
        x = np.argmax(last_col)  # get index of max
        path = path_trellis[x][-1]  # get the corresponding path
        ans.extend(path)

    return ans


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
    results = viterbi(sent_inds, pos_data, prior, transition, emission)
    write_results(test_file_name+'.pred', results)


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]
    # train_file_name = 'data/train-public'
    # test_file_name = 'data/test-public-small'
    # train_HMM(train_file_name)
    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
