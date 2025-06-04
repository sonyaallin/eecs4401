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

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during decoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')
    ####################
    # STUDENT CODE HERE
    ####################
    # PRIOR  
    prior = [0]*N_tags
    for i in sent_inds:
        word = pos_data[i][0]
        tag = pos_data[i][1]
        tag_i = UNIVERSAL_TAGS.index(tag)
        prior[tag_i] += 1
    prior = np.log(np.divide(prior, len(sent_inds)))

    # TRANSITION

    transition = np.zeros((N_tags, N_tags))
    trans_count = [0]*N_tags
    new_counter = {}
    for i in range(1, len(pos_data)):
        # If at the start of a sequence, don't check transition from last sequence's last word
        if i in sent_inds:
            continue 
        curr = pos_data[i]
        prev = pos_data[i-1]
        curr_tagi = UNIVERSAL_TAGS.index(curr[1])
        prev_tagi = UNIVERSAL_TAGS.index(prev[1])
        if (prev[1], curr[1]) in new_counter:
            new_counter[(prev[1], curr[1])] += 1
        else:
            new_counter[(prev[1], curr[1])] = 1
        transition[prev_tagi][curr_tagi] += 1
        trans_count[prev_tagi] += 1
    trans_count = np.array(trans_count)
    transition = np.log(transition / trans_count.reshape((N_tags, 1)))

    # EMISSION
    tag_counter = Counter(word[1] for word in pos_data)
    emission = {}
    for o in pos_data:
        word = o[0]
        tag = o[1]
        if (tag, word) not in emission:
            emission[(tag, word)] = 1
        else:
            emission[(tag, word)] += 1
    
    for key in emission.keys():
        tag = key[0]
        emission[key] = np.log(emission[key]/tag_counter[tag])

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
    sequence_start = 0

    while sequence_start < len(sent_inds):
        start = sent_inds[sequence_start]
        end = None

        # Last sequence index is the start of the last sequence which ends on pos_data[len(pos_data)]
        if sequence_start+1 == len(sent_inds):
            end = len(pos_data)
        else:
            end = sent_inds[sequence_start+1]
        
        prob_trellis = np.zeros((N_tags, end-start))
        path_trellis = np.zeros((N_tags, end-start), dtype=object)
        # Determine init trellis values
        # Offset pos_data indices by start always
        for i in range(N_tags):
            emissions = emission.get((UNIVERSAL_TAGS[i], pos_data[start]), np.log(0.00000000000000001))
            prob_trellis[i, 0] = prior[i] + emissions
            path_trellis[i, 0] = [UNIVERSAL_TAGS[i]]
        # Find most likely prior for each state
        for o in range(1, end-start):
            for s in range(N_tags):
                # Offset pos_data indices by start always
                emissions = emission.get((UNIVERSAL_TAGS[s], pos_data[start+o]), np.log(0.00000000000000001))
                argmax_p = None
                argmax = -1
                for i in range(N_tags):
                    p = prob_trellis[i, o-1] + transition[i, s] + emissions
                    if  argmax_p is None or p > argmax_p:
                        argmax_p = p
                        argmax = i
                prob_trellis[s, o] = prob_trellis[argmax, o-1] + transition[argmax, s] + emissions
                path_trellis[s, o] = path_trellis[argmax, o-1] + [UNIVERSAL_TAGS[s]]
        results.extend(path_trellis[np.argmax(prob_trellis[:, end-start-1]), end-start-1])
        sequence_start += 1
    
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