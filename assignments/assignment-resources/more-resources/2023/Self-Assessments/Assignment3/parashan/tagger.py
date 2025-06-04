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
    j = 0
    tag_inds = {UNIVERSAL_TAGS[i]: i for i in range(0, len(UNIVERSAL_TAGS))}
    priors = np.zeros(N_tags)    
    p_all_tags = np.zeros(N_tags)
    prev_all_tags = np.zeros(N_tags)
    transition = np.zeros((N_tags, N_tags))
    emission = {}
    for i in range(len(pos_data)):
        word, tag = pos_data[i]
        if(tag not in UNIVERSAL_TAGS):
            continue
        tag_ind = tag_inds[tag]
        p_all_tags[tag_ind] += 1 
        # compute emmission
        emission[(tag, word)] = emission.get((tag, word), 0) + 1
        if j < len(sent_inds) and i == sent_inds[j]:            
            priors[tag_ind] += 1 # compute counter
            j += 1
        else:
            prev_word, prev_tag = pos_data[i-1]
            prev_tag_ind = tag_inds[prev_tag]
            prev_all_tags[prev_tag_ind] += 1
            # compute transition
            transition[prev_tag_ind, tag_ind] += 1 
        # if i > 0:
        #     prev_word, prev_tag = pos_data[i-1]
        #     prev_tag_ind = tag_inds[prev_tag]
        #     prev_all_tags[prev_tag_ind] += 1
        #     # compute transition
        #     transition[prev_tag_ind, tag_ind] += 1 
            
    # compute the probabilities for prior and p_all_tags
    priors = priors / j
    priors = np.log(priors)
    p_all_tags = p_all_tags / len(pos_data)
    # compute the probabilities for transition
    # p(tag_j | tag_i) = p(tag_j, tag_i) / p(tag_i)
    transition = transition / prev_all_tags[:, np.newaxis]
    transition = np.log(transition)

    for key, value in emission.items():
        tag, word = key
        tag_ind = tag_inds[tag]
        ptag = p_all_tags[tag_ind]# P(tag)
        emission[key] = np.log((value / len(pos_data))/ptag) # P(tag, word)
    return priors, transition, emission
    

def compute_log_probability_word(word, emission, priors, tag_inds):
    # from defn of law of total probability
    # P (word) = sum over tags tag P(word and tag) = sum over all tags tag P(word | tag) * P(tag)
    total = 0
    
    for tag in UNIVERSAL_TAGS:
        tag_ind = tag_inds[tag]
        # log (P(word | tag) * P(tag)) = log(P(word|tag)) + log(P(tag))
        log_p_tag = emission.get((tag, word), np.log(0.0000001)) +  priors[tag_ind] 
        total += np.exp(log_p_tag) # we need it to be taken to exp
    
    return np.log(total)

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    ## Using the verison of forward algorithm from https://en.m.wikipedia.org/wiki/Forward_algorithm
    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################

    j = 0
    t = 0
    tag_inds = {UNIVERSAL_TAGS[i]: i for i in range(0, len(UNIVERSAL_TAGS))}
    results = []
    prev_log_p = np.zeros(N_tags)
    for i in range(len(pos_data)):
        word = pos_data[i]        
        best_tag = UNIVERSAL_TAGS[0]
        best_log = -1 * np.inf     
        
        if j < len(sent_inds) and i == sent_inds[j]:  
            prev_log_p = np.zeros(N_tags)
            # Base case compute log P(tag | word) = log (P(tag, word) / P(word)) 
            # = log (P(word | tag) * P(tag) / P(word)) = log(P(word | tag)) + log(P(tag)) - log (P(word)) 
            # = emission[(tag, word)] + prior[tag_ind] - compute_log_probability_word(word, emission, priors)
            log_p_word = compute_log_probability_word(word, emission, prior, tag_inds)
            for tag in UNIVERSAL_TAGS:
                tag_ind = tag_inds[tag]
                log_ptag_given_word = emission.get((tag, word), np.log(0.0000001)) + prior[tag_ind] - log_p_word
                # store exponentiated result in dp table so it can be used for the next word 
                prev_log_p[tag_ind] = log_ptag_given_word
                if log_ptag_given_word > best_log:
                    best_log = log_ptag_given_word
                    best_tag = tag
            results.append(best_tag)
            j += 1

        else:  
            # Alpha from this link: https://en.m.wikipedia.org/wiki/Forward_algorithm
            # p(tag | current word and all before) = 
            # p(tag, current word and all before)/p(current word and all before) = 
            # p(tag, current word and all before)/ 
            # sum over current tag p(tag, current and all words) = 
            # alpha_current(current) / sum over current alpha_current(current)
            # Compute alpha_current(current)
            alpha_current = np.zeros(N_tags)
            for tag in UNIVERSAL_TAGS: # loop over all tag options for alpha_current
                tag_ind = tag_inds[tag]
                tag_trans = transition[:, tag_ind]
                #Compute sum over prev p(current|prev)*alpha_prev(prev)
                alpha_sum = np.log(np.sum(np.exp(prev_log_p + tag_trans)))
                # Multiply p(word|current)
                log_prob = alpha_sum + emission.get((tag, word), np.log(0.0000001))
                # Store the tag's value
                alpha_current[tag_ind] = log_prob
            result = alpha_current - np.log(np.sum(np.exp(alpha_current)))
            best_tag = UNIVERSAL_TAGS[np.argmax(result)]
            prev_log_p = result           
            results.append(best_tag)         

    
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