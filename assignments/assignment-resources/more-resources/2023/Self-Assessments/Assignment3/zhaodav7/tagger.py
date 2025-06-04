# The tagger.py starter code for CSC384 A4.

import os
# from socket import send_fds
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

small_num = 0.0000000001
# nothing to see here
np.seterr(divide='ignore')

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
    pt_ind = 0
    prev_tag = None
    num_lines = len(sent_inds)
    tag_counts = [0 for _ in UNIVERSAL_TAGS]
    starting_pair_counts = [0 for _ in UNIVERSAL_TAGS]

    prior = [0 for _ in UNIVERSAL_TAGS]
    transition = [[0 for _ in UNIVERSAL_TAGS] for _ in UNIVERSAL_TAGS]
    emission = {}
    for tup in pos_data:
        cind = UNIVERSAL_TAGS.index(tup[1])
        tag_counts[cind] += 1
        new_tup = (tup[1], tup[0])
        if new_tup in emission.keys():
            emission[new_tup] += 1
        else:
            emission[new_tup] = 1
        
        if sent_inds != [] and pt_ind == sent_inds[0]:
            prior[cind] += 1
            prev_tag = None
            sent_inds.pop(0)
        
        if prev_tag is not None:
            pind = UNIVERSAL_TAGS.index(prev_tag)
            starting_pair_counts[pind] += 1
            transition[pind][cind] += 1
        prev_tag = tup[1]
        pt_ind += 1

    prior = np.divide(prior, num_lines)
    prior = np.log(prior)

    transition = [np.divide(transition[i], starting_pair_counts[i]) for i in range(len(transition))]
    transition = np.log(transition)


    for key in emission.keys():
        emission[key] /= tag_counts[UNIVERSAL_TAGS.index(key[0])]
        emission[key] = np.log(emission[key])

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
    num_lines = len(pos_data)
    num_tags = len(UNIVERSAL_TAGS)
    results=[]
    for j in range(len(sent_inds)):
        nl_ind = sent_inds[j]
        if nl_ind == sent_inds[-1]:
            line_size = num_lines-nl_ind
        else:
            line_size = sent_inds[j+1]-nl_ind
        
        prob_trellis = np.zeros((num_tags, line_size))
        path_trellis = [[[] for _ in range(line_size)] for _ in range(num_tags)]

        for s in range(num_tags):
            key = (UNIVERSAL_TAGS[s], pos_data[nl_ind])
            if key in emission.keys():
                prob_trellis[s][0] = prior[s] + emission[key]
            else:
                prob_trellis[s][0] = prior[s] + np.log(small_num)
            path_trellis[s][0].append(UNIVERSAL_TAGS[s])
        
        for o in range(1, line_size):
            for s in range(num_tags):
                key = (UNIVERSAL_TAGS[s], pos_data[nl_ind + o])
                if key in emission.keys():
                    x = np.argmax(prob_trellis[:,o-1] + transition[:, s] + emission[key])
                    prob_trellis[s][o] = prob_trellis[x][o-1] + transition[x][s] + emission[key]
                else:
                    x = np.argmax(prob_trellis[:,o-1] + transition[:, s] + (np.ones(num_tags) * np.log(small_num)))
                    prob_trellis[s][o] = prob_trellis[x][o-1] + transition[x][s] + np.log(small_num)
                path_trellis[s][o] += path_trellis[x][o-1][:]
                path_trellis[s][o].append(UNIVERSAL_TAGS[s])

        best_path_id = np.argmax(prob_trellis[:,-1])
        results += path_trellis[best_path_id][-1]

        # print("sentence number ", j, " at index ", nl_ind, "\n", path_trellis[best_path_id][-1])

    write_results(test_file_name+'.pred', results)
    # print(emission)

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
