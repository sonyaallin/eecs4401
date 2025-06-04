# The tagger.py starter code for CSC384 A4.

import math
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

    sentences = []
    for i in range(len(sent_inds)):
        if i == len(sent_inds) - 1:
            sentences.append(pos_data[sent_inds[i]:])
        else:
            sentences.append(pos_data[sent_inds[i]:sent_inds[i+1]])

    prior = []
    transition = []
    emission = {}
    tags = Counter(i[1] for i in pos_data)
    tags_at_start = Counter(pos_data[i][1] for i in sent_inds)
    len_of_words_tags = len(pos_data)
    len_of_indexes = len(sent_inds)

    for tag in UNIVERSAL_TAGS:
        occurence = tags_at_start[tag]
        if occurence == 0:
             prior.append(float('-inf'))
        else:
            prior.append(math.log(occurence / len_of_indexes))
    prior = np.array(prior)
    for i in range(len(UNIVERSAL_TAGS)):
        transition.append([])
        for j in range(len(UNIVERSAL_TAGS)):
            transition[i].append(float('-inf')) 

    next_occurences = Counter()

    for sentence in sentences:
        next_occurences.update(Counter((sentence[i][1], sentence[i+1][1])for i, value in enumerate(sentence[:-1])))
    
    tags_at_end = Counter(pos_data[i-1][1] for i in sent_inds[1:])
    tags_at_end.update({pos_data[-1][1] : 1})

    #print(next_occurences)
    for i, tag_i in enumerate(UNIVERSAL_TAGS):
        for j, tag_j in enumerate(UNIVERSAL_TAGS):
            occurence = next_occurences[(tag_i, tag_j)]
            if occurence != 0:
                transition[i][j] = math.log(occurence / (tags[tag_i] - tags_at_end[tag_i])) 
    transition = np.array(transition)
    tag_words = Counter((value[1], value[0]) for i, value in enumerate(pos_data))
    #print(tag_words)
    for tag_word_pair in tag_words:
            emission[tag_word_pair] = math.log(tag_words[tag_word_pair] / tags[tag_word_pair[0]])

    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')
    #print(emission)
    ####################
    # STUDENT CODE HERE
    ####################

    sentences = []
    for i in range(len(sent_inds)):
        if i == len(sent_inds) - 1:
            sentences.append(pos_data[sent_inds[i]:])
        else:
            sentences.append(pos_data[sent_inds[i]:sent_inds[i+1]])

    results = []
    for sentence in sentences: 
        prob_trellis = []
        path_trellis = []
        for i in range(len(UNIVERSAL_TAGS)):
            prob_trellis.append([])
            path_trellis.append([])
            for j in range(len(sentence)):
                prob_trellis[i].append(math.log(0.00001))
                path_trellis[i].append([])

        for s in range(len(UNIVERSAL_TAGS)):
            if ((UNIVERSAL_TAGS[s],sentence[0]) not in emission):
                emission_value = math.log(0.00001)
            else:
                emission_value = emission[(UNIVERSAL_TAGS[s],sentence[0])]
            prior_value = prior[s]
            if (prior_value == float('-inf')):
                prior_value = math.log(0.00001)

            prob_trellis[s][0] = prior_value + emission_value
            path_trellis[s][0] = [s]
        
   
        for o in range(1, len(sentence)):
            for s in range(len(UNIVERSAL_TAGS)):
                probs = {}
                for i, tag in enumerate(UNIVERSAL_TAGS):
                    if (((UNIVERSAL_TAGS[s],sentence[o]) not in emission)):
                        emission_value = math.log(0.00001)
                    else:
                        emission_value = emission[(UNIVERSAL_TAGS[s],sentence[o])]
                    transition_value = transition[i][s]
                    if (transition_value == float('-inf')):
                        transition_value = math.log(0.00001)
                    
                    probs[tag] = (prob_trellis[i][o -1]) + transition_value + emission_value

              
                x = max(probs, key=probs.get)

                prob_trellis[s][o] = probs[x]
                path_trellis[s][o] = path_trellis[UNIVERSAL_TAGS.index(x)][o-1] + [s]

        best_last_prob = prob_trellis[0][-1]
        best_last_tag = "VERB"
        for i, tag in enumerate(UNIVERSAL_TAGS[1:]):
            prob = prob_trellis[i][-1]
            if (prob > best_last_prob):
                best_last_prob = prob
                best_last_tag = tag

        path = path_trellis[UNIVERSAL_TAGS.index(best_last_tag)][-1]
        
        for i in range(0, len(sentence)):
            results.append(UNIVERSAL_TAGS[path[i]])

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