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
    prior = []
    transition = []
    emission = {}
    count_dict = Counter(pos_data)
    size = len(pos_data)
    total_sentences = len(sent_inds)
    prev_tag_idx = 0
    total_tags = []

    for i in range(N_tags):
        prior.append(0)
        total_tags.append(0)
        tmp_lst = []
        for j in range(N_tags):
            tmp_lst.append(0)
        transition.append(tmp_lst)

    start_sentence_index = sent_inds.pop(0)
    
    for i, word in enumerate(pos_data):
        idx = UNIVERSAL_TAGS.index(word[1])
        total_tags[idx] += 1
        if i == start_sentence_index:
            prior[idx] += 1
            if len(sent_inds) > 0:
                start_sentence_index = sent_inds.pop(0)
        else:
            transition[prev_tag_idx][idx] += 1
        prev_tag_idx = idx
    
    for i in range(N_tags):
        prior[i] = prior[i] / total_sentences
        tot = 0
        for j in range(N_tags):
            tot += transition[i][j]
        for j in range(N_tags):
            transition[i][j] = transition[i][j] / tot
    
    for key in count_dict.keys():
        idx = UNIVERSAL_TAGS.index(key[1])
        new_key = (key[1], key[0])
        emission[new_key] = np.log(count_dict[key] / total_tags[idx])

    prior = np.log(prior)
    transition = np.log(transition)

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

    prev_idx = 0
    start_idx = sent_inds.pop(0)
    sentence_idx = 0

    results = []
    prob_trellis = []
    path_trellis = []

    for i in range(len(pos_data)):
        word = pos_data[i]
        #print(word)
        if i == start_idx:
            if prob_trellis != []:
                max_idx = 0
                max_val = np.NINF
                for i in range(N_tags):
                    curr_val = prob_trellis[i][-1]
                    if curr_val > max_val:
                        max_val = curr_val
                        max_idx = i
                for r in path_trellis[max_idx][-1]:
                    results.append(UNIVERSAL_TAGS[r])
            sentence_idx = 0
            prev_idx = start_idx
            if len(sent_inds) > 0:
                start_idx = sent_inds.pop(0)
            else:
                start_idx = len(pos_data)
            if prev_idx != start_idx:
                prob_trellis = []
                path_trellis = []

                for a in range(N_tags):
                    tmp_probs = []
                    tmp_paths = []
                    for b in range(start_idx - prev_idx):
                        tmp_probs.append(0)
                        tmp_paths.append([])
                    prob_trellis.append(tmp_probs)
                    path_trellis.append(tmp_paths)
                
                for s in range(N_tags):
                    key = (UNIVERSAL_TAGS[s], word)
                    if key in emission:
                        prob_trellis[s][0] = prior[s] + emission[key]
                    else:
                        prob_trellis[s][0] = prior[s] - 30
                    path_trellis[s][0].extend([s])
        else:
            for s in range(N_tags):
                x = 0
                curr_max = np.NINF
                key = (UNIVERSAL_TAGS[s], word)
                if key in emission.keys():
                    for k in range(N_tags):
                        curr_val = prob_trellis[k][sentence_idx - 1] + transition[k][s] + emission[key]
                        if curr_val > curr_max:
                            x = k
                            curr_max = curr_val
                else:
                    for k in range(N_tags):
                        curr_val = prob_trellis[k][sentence_idx - 1] + transition[k][s] - 30
                        if curr_val > curr_max:
                            x = k
                            curr_max = curr_val
                prob_trellis[s][sentence_idx] = prob_trellis[x][sentence_idx - 1]
                path_trellis[s][sentence_idx] = path_trellis[x][sentence_idx - 1] + [s]
        sentence_idx += 1
    if prob_trellis != []:
        max_idx = 0
        max_val = np.NINF
        for i in range(N_tags):
            curr_val = prob_trellis[i][-1]
            if curr_val > max_val:
                max_val = curr_val
                max_idx = i
        for r in path_trellis[max_idx][-1]:
            results.append(UNIVERSAL_TAGS[r])
    
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