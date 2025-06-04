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

    # PRIOR
    prior = [0] * N_tags
    # loop through the start indices of all sequences to keep track of 
    # the number of times each tag is at the beginning of a sequence
    for ind in sent_inds:
        # increment tag for word at beginning of each sequence
        tag = (pos_data[ind])[1]
        prior[UNIVERSAL_TAGS.index(tag)] += 1
    # calculate log probability of each tag
    prior = np.divide(prior, len(sent_inds))
    prior = np.log(prior)

    # TRANSITION
    transition = np.zeros(shape=(N_tags, N_tags))
    # loop through all words to keep track of the number 
    # of times there is a transition between all tag pairs
    for index in range(len(pos_data)):
        # do not increment if we are at the start of a sequence
        if index not in sent_inds:
            # increment transiton between current and prev tag
            tag1 = (pos_data[index-1])[1]
            tag2 = (pos_data[index])[1]
            transition[UNIVERSAL_TAGS.index(tag1)][UNIVERSAL_TAGS.index(tag2)] += 1
    # calculate log probability of each tag pair
    transition = transition/transition.sum(axis=1)[:,None]
    transition = np.log(transition)

    # EMISSION
    emission = {}
    counter = [0] * N_tags
    # loop through all words to keep track of the number 
    # of times there is a tag, word pair in the input
    for pair in pos_data:
        word, tag = pair
        emission[(tag, word)] = emission.get((tag, word), 0) + 1
        # keep counter for each tag
        counter[UNIVERSAL_TAGS.index(tag)] += 1
    # loop through dictionary in order to calculate log probability of 
    # each tag, word pair(by using the counter array)
    for key, value in emission.items():
        emission[key] = np.log(value/counter[UNIVERSAL_TAGS.index(key[0])])

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
    # loop through the indices of the input words
    for word_ind in range(len(pos_data)):
        tag_prob = []
        # loop through the indices of the tags
        for tag_ind in range(N_tags):
            # get the emission of the current word, tag pair(or 0.00001 if we have not seen this word)
            curr_emm = emission.get((UNIVERSAL_TAGS[tag_ind],pos_data[word_ind]), 0.00001)
            # if we are predicting the first word in the sequence, we calculate the highest probability
            # of the current tag using the prior probabilities
            if word_ind == 0:
                tag_prob.append(prior[tag_ind] * curr_emm)
            # otherwise, we calculate the highest probability of the current tag by using all transition
            # probabilities and then applying argmax
            else:
                sequence_prob = []
                # use transition to get all probabilites for current tag
                for prev in range(N_tags):
                    sequence_prob.append(transition[prev,tag_ind] * curr_emm)
                # get tag index of the previous tag which gives the greatest probability
                prev_ind = np.argmax(sequence_prob)
                # find and append the greatest probability
                tag_prob.append(transition[prev_ind,tag_ind] * curr_emm)
        # get the tag with the highest probability at the current word position by using argmax,
        # then append it to the results
        results.append(UNIVERSAL_TAGS[np.argmax(tag_prob)])

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