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
    
    # Variable declaration
    prior = np.zeros(N_tags)
    transition = np.zeros((N_tags, N_tags))
    emission = {}

    # Obtain log prior probability
    for i in sent_inds:
        _, pos = pos_data[i]
        pos_id = UNIVERSAL_TAGS.index(pos)
        prior[pos_id] += 1
    prior = np.log(prior / np.sum(prior))

    # Obtain log emission probability 
    counter = Counter(pos_data)
    word_count = {}
    for key in counter:
        # word_tag -> Tag-Word
        flip_key = tuple(key)[::-1]
        emission[flip_key] = counter[key]
        # Update word count
        if key[1] not in word_count:
            word_count[key[1]] = counter[key]
        else:
            word_count[key[1]] += counter[key]
    for key in emission:
        emission[key] = np.log(emission[key] / word_count[key[0]])

    # Obtain log transition probability
    for i in range(len(pos_data)-1):
        if i + 1 not in sent_inds:
            _, pos = pos_data[i]
            _, next_pos = pos_data[i+1]
            pos_id = UNIVERSAL_TAGS.index(pos)
            next_pos_id = UNIVERSAL_TAGS.index(next_pos)
            transition[pos_id, next_pos_id] += 1
    transition = np.log(transition / np.reshape(np.sum(transition, axis=1), (N_tags, 1)))

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
    sentence_id = 0
    states = []
    for i in range(len(pos_data)):
        log_probs = []
        for j in range(len(UNIVERSAL_TAGS)):
            # Get log transition probability
            if i == sentence_id:
                log_trans_prob = transition[-1, j]
            else:
                log_trans_prob = transition[states[-1], j]
            # Get log emission probability
            key = (UNIVERSAL_TAGS[j], pos_data[i])
            log_emis_prob = emission[(UNIVERSAL_TAGS[j], pos_data[i])] if key in emission else -np.inf 
            # Track log state probability
            log_probs.append(log_trans_prob + log_emis_prob)
        # Find index (POS) with largest state probability
        max_state = np.argmax(log_probs)
        results.append(UNIVERSAL_TAGS[max_state])
        states.append(max_state)
        # Update sentence count
        if i == sentence_id:
            sentence_id += 1

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