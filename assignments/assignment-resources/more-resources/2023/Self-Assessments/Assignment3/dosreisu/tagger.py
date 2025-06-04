# The tagger.py starter code for CSC384 A4.

import os
import sys
from turtle import pos

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

    # Create dictionary for instant access to tag index
    tags = {}
    for i in range(len(UNIVERSAL_TAGS)):
        tags[UNIVERSAL_TAGS[i]] = i
    # Initalize
    prior = np.full(N_tags, 0)
    transition = np.full((N_tags, N_tags), 0)
    emission = {}
    # Variables
    pos = np.full(N_tags, 0) # To keep track of transition counts for each TAG
    inds = np.full(N_tags, 0) # To keep track of TAGs excluded from transition counts (eg end of sentence)
    prev = pos_data[0] # Keep track of previous pair
    sent_inds_index = 1 # Keep track of index within sent_inds
    # Adding some values to variables
    prior[tags[prev[1]]] += 1 # Need to include 1st value of sent_inds in prior
    inds[tags[pos_data[-1][1]]] += 1 # Need to include 1st value of sent_inds in inds
    emission[(prev[1], prev[0])] = 1 # Need to include 1st pair in emission

    for curr in range(1,len(pos_data[1:])+1):
        p = pos_data[curr] # Get the pair
        # Check if its a new sentence
        if sent_inds_index < len(sent_inds) and curr == sent_inds[sent_inds_index]:
            # New sentence so no transition and we update prior and inds
            inds[tags[prev[1]]] += 1
            prior[tags[p[1]]] += 1
            sent_inds_index += 1
        else:
            # Old sentense so we can count a transition
            transition[tags[prev[1]]][tags[p[1]]] += 1
            pos[tags[prev[1]]] += 1
        # Update emission counts
        emission[(p[1], p[0])] = emission.get((p[1], p[0]), 0) + 1
        # Set previous to current
        prev = p
    # Calculate log probabilities
    prior = np.log(prior / len(sent_inds))
    transition = np.log(transition.T / pos).T
    pos += inds
    for k in emission:
        emission[k] = np.log(emission[k] / pos[tags[k[0]]])

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

    # Update sent_inds to include an index bigger than len(pos_data) for use in the for loop
    sent_inds.append(len(pos_data)+1)

    # Initialize variables
    results = [] # Will keep results (predicted TAGS)
    prev = 0 # Will keep track of where the current sentence starts
    for i in sent_inds[1:]: # Iterate through all sentences in the test set
        sentence = pos_data[prev:i]

        # Viterbi Algorithm
        # Initialization for Viterbi
        prob_trellis = np.empty((len(UNIVERSAL_TAGS),len(sentence)))
        # Set all values in path trellis to current TAG so that it doesn't have to be done in the other for loop
        path_trellis = [ [[c]] * len(sentence) for c in range(len(UNIVERSAL_TAGS))]
        for s in range(len(UNIVERSAL_TAGS)):
            # Probabilities are stored as logs so we use +
            prob_trellis[s, 0] = prior[s] + emission.get((UNIVERSAL_TAGS[s], sentence[0]), np.log(0.000001)) 
        # Loop through the words and complete the trellis
        for o in range(1, len(sentence)):
            for s in range(len(UNIVERSAL_TAGS)):
                m = float('-inf'), s
                for x in range(len(UNIVERSAL_TAGS)):
                    # Probabilities are stored as logs so we use +
                    value = prob_trellis[x, o-1] + transition[x][s] + emission.get((UNIVERSAL_TAGS[s],sentence[o]), np.log(0.000001))
                    if m[0] < value:
                        m = value, x
                prob_trellis[s,o] = m[0]
                path_trellis[s][o] = path_trellis[m[1]][o-1] + [s]

        # Restore the path from the trellis and append the TAGS to results
        results.extend(np.take(UNIVERSAL_TAGS, path_trellis[np.argmax(prob_trellis, axis=0)[-1]][-1]))

        # Update the start of the next sentence
        prev = i
    
    # Write results to file
    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # pos_data = read_data_train(train_file_name+'.txt')
    # sent_inds = read_data_ind(train_file_name+'.ind')
    # print(sent_inds)

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
    # sol = read_data_test(test_file_name+'.soln')
    # pred = read_data_test(test_file_name+'.pred')
    # right = 0
    # print(len(pred))
    # print(len(sol))
    # for i in range(len(pred)):
    #     right += (pred[i] == sol[i])
    # print(right, len(pred), right/len(pred))