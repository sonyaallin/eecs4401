# The tagger.py starter code for CSC384 A4.

import os
import sys

import math
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

def estimate_prior(pos_data, sent_inds):
    """
    Returns a numpy array of estimated prior log probabilities.
    """

    prior = np.zeros(N_tags)

    # Initialize counter of seeing tags at the beginning of a sequence
    tag_counter = Counter()

    # Count tags for the counter
    for sent_ind in sent_inds:
        pair = pos_data[sent_ind]
        tag = pair[1]
        tag_counter[tag] += 1
    
    total_tags = sum(tag_counter.values())
 
    # Estimate probabilities
    for i, tag in enumerate(UNIVERSAL_TAGS):
        if tag_counter[tag] == 0 or total_tags == 0:
            prior[i] = -math.inf
        else:
            prior[i] = math.log(tag_counter[tag]/total_tags)

    return prior

def estimate_transition(pos_data, sent_inds):
    """
    Returns a numpy array of estimated transition log probabilities.
    """

    transition = np.zeros((N_tags, N_tags))

    # Initialize counters of seeing tags given it is a transition from another tag in a sequence
    transition_counter = {}
    for tag in UNIVERSAL_TAGS:
        transition_counter[tag] = Counter()

    # Count tags for the counters
    for i, sent_ind in enumerate(sent_inds):
        if len(sent_inds[i+1:]) != 0:
            next_sent_ind = sent_inds[i+1]
        else:
            next_sent_ind = len(pos_data)

        prev_pair = pos_data[sent_ind]
        for curr_pair in pos_data[sent_ind+1:next_sent_ind]:
            prev_tag = prev_pair[1]
            curr_tag = curr_pair[1]
            transition_counter[prev_tag][curr_tag] += 1
            prev_pair = curr_pair

    # Estimate probabilities
    for i, given_tag in enumerate(UNIVERSAL_TAGS):
        total_transitions = sum(transition_counter[given_tag].values())
        for j, tag in enumerate(UNIVERSAL_TAGS):
            if transition_counter[given_tag][tag] == 0 or total_transitions == 0:
                transition[i][j] = -math.inf
            else:
                transition[i][j] = math.log(transition_counter[given_tag][tag]/total_transitions)

    return transition

def estimate_emission(pos_data):
    """
    Returns a numpy array of estimated emission log probabilities.
    """

    emission = {}

    # Initialize counters of seeing words given it is paired with a tag
    emission_counter = {}
    for tag in UNIVERSAL_TAGS:
        emission_counter[tag] = Counter()

    # Count words
    for pair in pos_data:
        word = pair[0]
        tag = pair[1]
        emission_counter[tag][word] += 1

    # Estimate probabilities
    for tag in UNIVERSAL_TAGS:
        total_words = sum(emission_counter[tag].values())
        for word in emission_counter[tag].keys():
            emission[(tag, word)] = math.log(emission_counter[tag][word]/total_words)

    return emission

def viterbi(pos_data, prior, transition, emission):
    """
    Run Viterbi algorithm on the given sentence and output tags.
    """

    prob_trellis = np.zeros((N_tags, len(pos_data)))
    path_trellis = np.zeros((N_tags, len(pos_data)), dtype=np.int64)

    for i, tag in enumerate(UNIVERSAL_TAGS):
        word = pos_data[0]
        prob_trellis[i][0] = prior[i] + emission.get((tag, word), math.log(1e-5))
        path_trellis[i][0] = i

    for i, word in enumerate(pos_data[1:], 1):
        for j, tag in enumerate(UNIVERSAL_TAGS):
            # Find the tag index that maximizes probability
            probs = np.zeros(N_tags)
            for k in range(N_tags):
                probs[k] = prob_trellis[k][i-1] + transition[k][j] + emission.get((tag, word), math.log(1e-5))
            x = np.argmax(probs)

            prob_trellis[j][i] = prob_trellis[x][i-1] + transition[x][j] + emission.get((tag, word), math.log(1e-5))
            path_trellis[j][i] = x

    # Find the tag index that maximizes sequence probability
    probs = np.zeros(N_tags)
    for i in range(N_tags):
        probs[i] = prob_trellis[i][len(pos_data)-1]
    x = np.argmax(probs)

    # Go through the path trellis to get the tags for the sequence
    tags = []
    for i in range(len(pos_data)-1, -1, -1):
        tags.append(UNIVERSAL_TAGS[x])
        x = path_trellis[x][i]

    return reversed(tags)

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

    prior = estimate_prior(pos_data, sent_inds)
    transition = estimate_transition(pos_data, sent_inds)    
    emission = estimate_emission(pos_data)

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

    for i, sent_ind in enumerate(sent_inds):
        if len(sent_inds[i+1:]) != 0:
            next_sent_ind = sent_inds[i+1]
        else:
            next_sent_ind = len(pos_data)

        tags = viterbi(pos_data[sent_ind:next_sent_ind], prior, transition, emission)
        results += tags

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