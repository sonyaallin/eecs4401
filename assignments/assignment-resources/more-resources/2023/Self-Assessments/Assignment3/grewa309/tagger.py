# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter
# import time

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
    transition_table= {}
    emission_table = {}
    prior_table = Counter()
    tag_to_index_mapping = {UNIVERSAL_TAGS[i]:i for i in range(N_tags)}

    prior = []
    transition = np.full((N_tags, N_tags), np.inf * -1)
    emission = {}

    # Update prior table 
    for i in sent_inds:
        prior_table[pos_data[i][1]] += 1
    

    #intialize emission_table and transition_table
    for i in range(N_tags):
        emission_table[UNIVERSAL_TAGS[i]] = Counter()
        transition_table[UNIVERSAL_TAGS[i]] = Counter()

    # loop over all elements in the pos_data and update the emission and transition tables
    for i in range(len(sent_inds)):
        end_index = sent_inds[i + 1] if i + 1 < len(sent_inds) else len(pos_data)
        prev_tag = None
        for j in range(sent_inds[i], end_index):
            word = pos_data[j][0]
            tag = pos_data[j][1]

            emission_table[tag][word] += 1

            if prev_tag:
                transition_table[prev_tag][tag] += 1
            
            prev_tag = tag

    # update prior with the prob of a tag being the first word in a sequence
    for i in range(N_tags):
        tag = UNIVERSAL_TAGS[i]
        prior.append(np.log(prior_table[tag] / len(sent_inds)))
    
    
    #Update emissions with probabilities of a word given a tag
    for tag in emission_table:
        x = sum(emission_table[tag].values())
        for word in emission_table[tag]:
            emission[(tag, word)] = np.log(emission_table[tag][word] / x)

    #Update transitions with probabilities of a tag given a previous tag
    for prev_tag in transition_table:
        x = sum(transition_table[prev_tag].values())
        for tag in transition_table[prev_tag]:
            prev_tag_index = tag_to_index_mapping[prev_tag]
            tag_index = tag_to_index_mapping[tag]
            transition[prev_tag_index][tag_index] = np.log(transition_table[prev_tag][tag] / x)

    return np.array(prior), transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    # t1 = time.time()
    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')


    ####################
    # STUDENT CODE HERE
    ####################

    # have all the paramters for a hmm, now can use Viterbi algorithm on the test data
    # to calcualte the most sequence of tags for the given sequence of emissions

    results = []
    tag_indexes = list(range(len(UNIVERSAL_TAGS)))
    
    for i in range(len(sent_inds)):
        sent_start_index = sent_inds[i]
        sent_end_index = sent_inds[i + 1] if i + 1 < len(sent_inds) else len(pos_data)
        prob_trellis, path_trellis = viterbi(pos_data[sent_start_index: sent_end_index], UNIVERSAL_TAGS, prior, transition, emission)
        x = max(tag_indexes, key=lambda v: prob_trellis[-1][v])
        results.extend(path_trellis[-1][x])
    
    write_results(test_file_name+'.pred', results)
    # t2 = time.time()
    # print(t2 - t1)
    return


def viterbi(states, possible_tags, prior_probs, transition_probs, emission_probs):
    
    prob_trellis = np.zeros((len(states), len(possible_tags)))
    path_trellis = []

    temp = []
    for i in range(len(possible_tags)):
        prob_trellis[0][i] = prior_probs[i] + emission_probs.get((possible_tags[i], states[0]),  np.log(0.000001))
        temp.append([possible_tags[i]])
    
    path_trellis.append(temp)

    # update the path and prob trellis for rest of the states
    lst= list(range(len(possible_tags)))
    for i in range(1, len(states)):
        temp = []
        for j in range(len(possible_tags)):
            x = max(lst, key=lambda v: prob_trellis[i - 1][v] + transition_probs[v][j] + emission_probs.get((possible_tags[j], states[i]), np.log(0.000001)))
            prob_trellis[i][j] = prob_trellis[i - 1][x] + transition_probs[x][j] + emission_probs.get((possible_tags[j], states[i]), np.log(0.000001)) 
            temp.append(path_trellis[i-1][x] + [possible_tags[j]])
        
        path_trellis.append(temp)


    return prob_trellis, path_trellis


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