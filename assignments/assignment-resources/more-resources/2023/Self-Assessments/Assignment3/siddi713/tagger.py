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

UNIVERSAL_TAGS_MAPPING = {
    "VERB" : 0,
    "NOUN" : 1,
    "PRON" : 2,
    "ADJ" : 3,
    "ADV" : 4,
    "ADP" : 5,
    "CONJ" : 6,
    "DET" : 7,
    "NUM" : 8,
    "PRT" : 9,
    "X" : 10,
    "." : 11,
}

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
    prior = np.ones(N_tags) * -np.inf
    transition = np.ones((N_tags, N_tags)) * -np.inf
    emission = {}

    total_tags = len(pos_data)
    num_of_starting_tags = len(sent_inds)
    num_of_tag_occurences, num_of_prev_tag_occurences, starting_tags, temp_trasition = {}, {}, {}, {}
    current_start_posistion = 0
    for index, data in enumerate(pos_data):
        word, tag = data
        num_of_tag_occurences[tag] = num_of_tag_occurences.get(tag, 0) + 1
        # Record data for prior
        if current_start_posistion < len(sent_inds) and index == sent_inds[current_start_posistion]:
            starting_tags[tag] = starting_tags.get(tag, 0) + 1
            current_start_posistion += 1
        else:
            # Record data for transition
            prev_tag = pos_data[index-1][1]
            transition_key = (prev_tag, tag)
            temp_trasition[transition_key] = temp_trasition.get(transition_key, 0) + 1
            num_of_prev_tag_occurences[prev_tag] = num_of_prev_tag_occurences.get(prev_tag, 0) + 1

        # Record data for emission
        emission_key = (tag, word)
        emission[emission_key] = emission.get(emission_key, 0) + 1
    
    # Calculate prior
    for tag in starting_tags:
        prior[UNIVERSAL_TAGS_MAPPING[tag]] = np.log(starting_tags[tag]/num_of_starting_tags)
    
    # Calculate transition
    total_transitions = total_tags - num_of_starting_tags # We don't need to count the transitions from the start tags
    for key in temp_trasition:
        p_of_a_and_b = temp_trasition[key] / total_transitions
        p_of_b = num_of_prev_tag_occurences[key[0]] / total_transitions
        transition[UNIVERSAL_TAGS_MAPPING[key[0]], UNIVERSAL_TAGS_MAPPING[key[1]]] = np.log(p_of_a_and_b / p_of_b)
    
    # Calculate emission
    for key in emission:
        p_of_a_and_b = emission[key] / total_tags
        p_of_b = num_of_tag_occurences[key[0]] / total_tags
        emission[key] = np.log(p_of_a_and_b / p_of_b)
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
    current_start_posistion = 0
    def compute_total_word_prob(word):
        total_word_prob = 0
        for tag in UNIVERSAL_TAGS:
            # Emmission and prior log probabilities, need to handle them according to log laws and convert to a regular probability so we can log the entire sum
            total_word_prob += np.exp(emission.get((tag, word), np.log(0.00001)) + prior[UNIVERSAL_TAGS_MAPPING[tag]])
        return np.log(total_word_prob)
    
    def compute_tag_with_highest_prob(word, pword):
        max_prob = -np.inf
        max_tag = UNIVERSAL_TAGS[0]
        probs = np.zeros(N_tags)
        for tag in UNIVERSAL_TAGS:
            # Emmission, prior and pword are all log probabilities, need to handle them according to log laws
            # This should be equal to P(word|tag) * P(tag) / P(word)
            prob = emission.get((tag, word), np.log(0.00001)) + prior[UNIVERSAL_TAGS_MAPPING[tag]] - pword
            probs[UNIVERSAL_TAGS_MAPPING[tag]] = prob
            if prob > max_prob:
                max_prob = prob
                max_tag = tag
        return max_tag, probs
    
    # Forward Algorithm
    def compute_tag_with_highest_prob_with_previous_values(word, probs):
        alpha_probs, new_probs = [], []
        max_alpha = -np.inf
        max_tag = UNIVERSAL_TAGS[0]
        for index_i, tag_i in enumerate(UNIVERSAL_TAGS):
            p_word_given_tag = emission.get((tag_i, word), np.log(0.00001))
            alpha_t = 0
            for index_j, tag_j in enumerate(UNIVERSAL_TAGS):
                p_prev_tag = transition[index_j, index_i]
                alpha_prev_tag = probs[index_j]
                alpha_t += np.exp(p_prev_tag + alpha_prev_tag)
            
            alpha_t = np.log(alpha_t) + p_word_given_tag 
            alpha_probs.append((alpha_t, tag_i))

        alpha_probs_sum = 0 
        for aprob in alpha_probs:
            alpha_probs_sum += np.exp(aprob[0])
        alpha_probs_sum = np.log(alpha_probs_sum)

        for aprob in alpha_probs:
            alpha = aprob[0] - alpha_probs_sum
            if alpha > max_alpha:
                max_alpha = alpha
                max_tag = aprob[1]
            new_probs.append(alpha)

        return max_tag, new_probs

    all_probs = []
    for index, word in enumerate(pos_data):
        # Start of sentence 
        if current_start_posistion < len(sent_inds) and index == sent_inds[current_start_posistion]:
            all_probs = []
            total_prob = compute_total_word_prob(word)
            max_tag, all_probs = compute_tag_with_highest_prob(word, total_prob)
            results.append(max_tag)
            current_start_posistion += 1
        # Remainder of sentence
        else:
            max_tag, all_probs = compute_tag_with_highest_prob_with_previous_values(word, all_probs)
            results.append(max_tag)


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
    tag(train_file_name, test_file_name)