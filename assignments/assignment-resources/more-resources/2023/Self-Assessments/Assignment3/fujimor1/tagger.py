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

    pos_data = np.array(pos_data)
    
    # prior
    prior = []
    counter = Counter(pos_data[sent_inds, 1])
    total = sum(counter.values())
    for tag in UNIVERSAL_TAGS:
        prior.append(np.log(counter[tag] / total))
    prior = np.array(prior)

    # transition
    transition = np.zeros((len(UNIVERSAL_TAGS), len(UNIVERSAL_TAGS)))
    for tag in UNIVERSAL_TAGS:
        # count the frequency of next tag
        next_tag_counter = dict.fromkeys(UNIVERSAL_TAGS, 0)
        for i, (_, ele) in enumerate(pos_data[:-1]):
            # skip if the iterator is at the end of sentences
            if i+1 in sent_inds:
                continue
            # update counter
            elif ele == tag:
                next_tag_counter[pos_data[i+1][1]] += 1
        
        # update transition matrix
        i = UNIVERSAL_TAGS.index(tag)
        total = sum(next_tag_counter.values())
        for next_tag, freq in next_tag_counter.items():
            j = UNIVERSAL_TAGS.index(next_tag)
            if freq == 0:
                transition[i, j] = -np.inf
            else:
                transition[i, j] = np.log(freq / total)

    # emission
    emission = {}
    for tag in UNIVERSAL_TAGS:
        counter = Counter(pos_data[np.where(pos_data[:, 1] == tag)[0]][:, 0])
        total = sum(counter.values())
        for word, freq in counter.items():
            emission[(tag, word)] = np.log(freq / total)
        
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

    # run viterbi for each sentence
    for i in range(len(sent_inds)):
        try:
            sent = pos_data[sent_inds[i]:sent_inds[i+1]]
        except IndexError:
            sent = pos_data[sent_inds[i]:]

        # initialize trellis
        prob_trellis = np.zeros((len(prior), len(sent)))
        path_trellis = {}

        # determine trellis values for tag_1
        for i in range(len(prior)):
            if (UNIVERSAL_TAGS[i], sent[0]) not in emission:
                emission_prob = np.log(1e-8)
            else:
                emission_prob = emission[(UNIVERSAL_TAGS[i], sent[0])]
            prob_trellis[i, 0] = prior[i] + emission_prob
            path_trellis[(i, 0)] = [i]

        # determine trellis values for tag_2 ... tag_t
        for o in range(1, len(sent)):
            for i in range(len(prior)):
                max_prev_i = np.argmax([prob_trellis[prev_i, o-1] + transition[prev_i, i] for prev_i in range(len(prior))])
                if (UNIVERSAL_TAGS[i], sent[o]) not in emission:
                    emission_prob = np.log(1e-8)
                else:
                    emission_prob = emission[(UNIVERSAL_TAGS[i], sent[o])]
                prob_trellis[i, o] = prob_trellis[max_prev_i, o-1] + transition[max_prev_i, i] + emission_prob
                path_trellis[(i, o)] = path_trellis[(max_prev_i, o-1)] + [i]

        # obtain most likely sequence of tags
        results += path_trellis[(np.argmax(prob_trellis[:, -1]), len(sent)-1)]

    # convert indices to tags
    results = [UNIVERSAL_TAGS[i] for i in results]

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