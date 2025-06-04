# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter, defaultdict

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

    total_inds = len(sent_inds)
    total_tags = len(pos_data)

    # PRIOR #
    # Dictionary whose keys are tags, values correspond to the number of times a given tag appears at the beginning of a sentence
    prior_dict = Counter()
    prior = np.zeros(N_tags)
    
    # Increment count of tags given they are in sent_inds list
    for index in sent_inds:
        prior_dict[pos_data[index][1]] += 1
    # Set log prior probabilities for each tag
    for i in range(N_tags):
        prior[i] = np.log(prior_dict[UNIVERSAL_TAGS[i]] / total_inds)


    # TRANSITION #
    transition = np.zeros((N_tags, N_tags))
    # Keys are transitions, values are count of transition
    transition_dict = Counter()
    # Keys are tags, values are count of tag across whole dataset
    tag_dict = Counter()

    # Populate transition and tag dictionaries (don't need last word as it cannot transition to any word)
    for i in range(total_tags - 1):
        transition_dict[(pos_data[i][1], pos_data[i+1][1])] += 1
        tag_dict[pos_data[i][1]] += 1

    # Decrement counts if transitioning into new sequence, or if the last word in a sequence
    for i in sent_inds[1:]:
        transition_dict[(pos_data[i-1][1], pos_data[i][1])] -= 1 # Transition (seq1, seq2)
        tag_dict[pos_data[i-1][1]] -= 1 # Last word in sequence

    # Prob of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
    for i in range(N_tags):
        for j in range(N_tags):
            transition[i][j] = np.log(transition_dict[(UNIVERSAL_TAGS[i], UNIVERSAL_TAGS[j])] / tag_dict[UNIVERSAL_TAGS[i]])
    

    # EMISSION #
    # Keys are (TAG, WORD), values are the number of times this combination appears
    emission_dict = Counter()
    emission = {}
    # Keys are words/tags, values are number of times words/tags appear
    words = Counter()
    tags = Counter()

    # Count number of time words/tags appear
    for line in pos_data:
        words[line[0]] += 1
        tags[line[1]] += 1
        emission_dict[(line[1], line[0])] += 1

    # P(w|t) = P(wnt)/p(t) - find log emission probability
    for line in pos_data:
        emission[(line[1], line[0])] = np.log((emission_dict[(line[1], line[0])] / total_tags) / (tags[line[1]] / total_tags))

    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    # Retrieve initial probabilities
    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    # Store predictions, partitioned sequences, and possible tag indices
    results = []
    sequences = []
    tag_inds = [i for i in range(N_tags)]

    # Partition data set into setences to form and populate sequences
    for i in range(len(sent_inds) - 1):
            sequences.append(pos_data[sent_inds[i]: sent_inds[i+1]])
    # The last sequence proceeds to the end of the file
    sequences.append(pos_data[sent_inds[-1]:])

    # Begin tagging sequences individually
    for seq in sequences:
        prob_trellis = np.zeros((N_tags, len(seq)))
        path_trellis = np.zeros((N_tags, len(seq)), dtype=object)

        # Set trellis values for X_1 or first word in sequence
        for s in range(N_tags):
            # If word hasn't been seen, give it a small probability and add to emissions
            if (UNIVERSAL_TAGS[s], seq[0]) not in emission.keys():
                emission[(UNIVERSAL_TAGS[s], seq[0])] = np.log(0.000001)
            
            prob_trellis[s][0] = prior[s] + emission[(UNIVERSAL_TAGS[s], seq[0])]
            path_trellis[s][0] = [s]
            
        # Populate path and prob trellis with HMM chaining algorithm (modified Viterbi)
        for o in range(1, len(seq)):
            for s in range(N_tags):
                if (UNIVERSAL_TAGS[s], seq[o]) not in emission.keys():
                    emission[(UNIVERSAL_TAGS[s], seq[o])] = np.log(0.000001)
                # Find the index of the path whose probability is maximum across all tags from the previous time point
                x = np.argmax([prob_trellis[x][o-1] + transition[x][s] + emission[(UNIVERSAL_TAGS[s], seq[o])] for x in tag_inds])
                # Set current time point tag to have the probability found above
                prob_trellis[s][o] = prob_trellis[x][o-1] + transition[x][s] + emission[(UNIVERSAL_TAGS[s], seq[o])]
                # Copy path from previous time point into new time point in path_trellis
                prev_list = path_trellis[x][o-1].copy()
                prev_list.append(s)
                path_trellis[s][o] = prev_list
        
        # Contains the probabilities of last timepoint across all prob_trellis
        prob_list = []

        # Populate prob_list with all probabilities at last timepoint
        for tag_prob in prob_trellis:
            prob_list.append(tag_prob[-1])

        # Extract highest probability path
        final_tag_inds = path_trellis[np.argmax(prob_list)][-1]

        # Translate from indices to tags from UNIVERSAL_TAGS and populate results
        for index in final_tag_inds:
            results.append(UNIVERSAL_TAGS[index])
    
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