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
    with open(path, 'w+') as f:
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

    ### PRIOR ###
    np_pos_data, np_sent_inds = np.array(pos_data), np.array(sent_inds)
    count = Counter(np_pos_data[np_sent_inds][:, 1])
    prior = np.array([count[UNIVERSAL_TAGS[i]] for i in range(N_tags)], dtype=float)
    temp = prior != 0 # Used to avoid divide by zero error
    prior /= np.sum(prior)
    prior = np.log(prior, where=temp)
    prior[np.logical_not(temp)] = -np.inf  # Setting the proper values for np.log(0)

    ### PRIOR ###

    ### TRANSITION ###    
    transition = np.zeros((N_tags, N_tags))
    prev_ind_tag = UNIVERSAL_TAGS.index(np_pos_data[0][1])

    for i in range(1, len(np_pos_data)):
        tag = np_pos_data[i][1]
        ind_tag = UNIVERSAL_TAGS.index(tag)
        if i not in np_sent_inds:
            transition[prev_ind_tag][ind_tag] += 1 # Will add to the probabilty of P(tag_j and tag_i)

        prev_ind_tag = ind_tag
    
    temp = transition != 0 # Used to avoid divide by zero error
    transition /= np.array([np.sum(transition, axis=1)]).T # P(tag_j|tag_i) =  P(tag_j and tag_i) / P(tag_i)
    transition = np.log(transition, where=temp)
    transition[np.logical_not(temp)] = -np.inf # Setting the proper values for np.log(0)
    ### TRANSITION ###

    ### EMISSION ###
    emission = Counter(pos_data)
    count = Counter(np_pos_data[:, 1])
    emission = {(k[::-1]):np.log(v/count[k[1]]) for k, v in emission.items()}
    ### EMISSION ###

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
    results = []

    ### WORD LIST ###
    word_list = {}
    for tag, word in emission.keys():
        if word in word_list:
            word_list[word].append(tag)
        else:
            word_list[word] = [tag]
    
    for k, v in word_list.items(): # Get the most common tag given to the word
        word_list[k] = Counter(v).most_common(1)[0][0]
    ### WORD LIST ###

    for i in range(len(pos_data)):
        if pos_data[i] in word_list: # Word Used In Train Data
            results.append(word_list[pos_data[i]])
        else:
            if i in sent_inds: # New Sentence
                tag_ind = np.argmax(prior)
                results.append(UNIVERSAL_TAGS[tag_ind])
            else: # In the middle of a Sentence
                prev_tag_ind = UNIVERSAL_TAGS.index(results[-1])
                tag_ind = np.argmax(transition[prev_tag_ind, :])
                results.append(UNIVERSAL_TAGS[tag_ind])
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