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

    prior = np.array(generate_prior(pos_data, sent_inds))
    transition = np.array(generate_transition(pos_data, sent_inds))
    emission = generate_emission(pos_data, sent_inds)
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

    result = []
    for data in pos_data:
        temp = []
        for key, value in emission.items():
            if data == key[1]:
                temp.append([key[0], value])
        result.append(temp)
    results = []
    for ind in range(len(pos_data)):
        data = pos_data[ind]
        re = result[ind]
        if len(re) == 1:
            results.append(re[0][0])
        else:
            if ind in sent_inds:  # meaning it is the start of the sentence
                all_possibilities = []  
                for p in re:
                    if p[0] in UNIVERSAL_TAGS:
                        p_ind = UNIVERSAL_TAGS.index(p[0])
                        if p_ind < len(prior):
                            all_possibilities.append([p[0], prior[p_ind]*p[1]])  # multiply prior and emission p to get the most possible soln
                # go through all p, and get the answer
                if all_possibilities != []:
                    min_p = all_possibilities[0][1]
                    min_tag = all_possibilities[0][0]
                    for p in all_possibilities:
                        if p[1] < min_p:
                            min_tag = p[0]
                            min_p = p[1]
                    results.append(min_tag)
                # word does not appear in training data, assign it to the first one in UNIVERSAL TAG for convenience
                else:
                    max_tag = UNIVERSAL_TAGS[0]
                    results.append(max_tag)
            else: # not the start of the sentence
                last_tag = results[-1]
                last_tag_ind = UNIVERSAL_TAGS.index(last_tag)
                all_possibilities = []  
                for p in re:
                    if last_tag_ind < len(transition):
                        curr_tags_transition = transition[last_tag_ind] # got the last tag places
                        if p[0] in UNIVERSAL_TAGS:
                            tag_ind = UNIVERSAL_TAGS.index(p[0])
                            if tag_ind < len(curr_tags_transition):
                                all_possibilities.append([p[0], curr_tags_transition[tag_ind]*p[1]])
                # go through all p, and get the answer
                if all_possibilities != []:
                    min_p = all_possibilities[0][1]
                    min_tag = all_possibilities[0][0]
                    for p in all_possibilities:
                        if p[1] < min_p:
                            min_tag = p[0]
                            min_p = p[1]
                    results.append(min_tag)
                else:
                    # find the last one's tag and search it in transition for highest prob
                    if last_tag_ind < len(transition):
                        curr_tags_transition = transition[last_tag_ind]
                        max_p_ind = np.argmax(curr_tags_transition)
                        if max_p_ind < len(UNIVERSAL_TAGS):
                            max_p_tag = UNIVERSAL_TAGS[max_p_ind]
                        else:
                            max_p_tag = UNIVERSAL_TAGS[0]
                        results.append(max_p_tag)
                    else:
                        max_p_tag = UNIVERSAL_TAGS[0]
                        results.append(max_p_tag)

    write_results(test_file_name+'.pred', results)

def generate_prior(pos_data, sent_inds):
    """
    Helper function to generate prior tables. 
    """
    total_number = len(sent_inds)
    tags_p = {}

    for ind in sent_inds:
        curr_pair = pos_data[ind]
        t = curr_pair[1]
        if t in tags_p:
            tags_p[t] += 1
        else:
            tags_p[t] = 1

    prior = []
    for tag in UNIVERSAL_TAGS:
        prior.append(np.log(tags_p[tag]/total_number))
    return prior

def generate_transition(pos_data, sent_inds):
    """
    Helper function to generate transition tables.
    """
    result = []
    sent_indss = sent_inds[:]
    sent_indss.append(len(pos_data))
    for ind in range(N_tags):  # tag i
        result.append({})
        p_given_tag = result[ind]
        tag_given = UNIVERSAL_TAGS[ind]
        total_count = 0
        temp = {}
        curr_ind = 0
        for sent_ind in sent_indss:  # go through all sentences
            while curr_ind < sent_ind:  # iterate through current sentence
                curr = pos_data[curr_ind]
                if curr_ind + 1 < sent_ind:  # count of tag i do not include last word of sentence
                    next_curr = pos_data[curr_ind + 1]
                    if curr[1] == tag_given:  # verify tag i matched
                        total_count += 1  # increment denominator
                        # increment numerator
                        if next_curr[1] not in temp:
                            temp[next_curr[1]] = 1
                        else:
                            temp[next_curr[1]] += 1
                curr_ind += 1
        for tag in UNIVERSAL_TAGS: # tag j
            if tag not in temp:
                p_given_tag[tag] = [0, total_count, -np.inf]
            else:
                p_given_tag[tag] = [temp[tag], total_count, np.log(temp[tag]/total_count)]
    answer = []
    # extract the log probablity and return them
    for each_tag in range(len(result)): 
        temp = []
        for t in UNIVERSAL_TAGS:
            temp.append(result[each_tag][t][2])
        answer.append(np.array(temp))
    return answer

def generate_total_count(pos_data, sent_inds):
    result = {}
    sent_indss = sent_inds[:]
    sent_indss.append(len(pos_data))
    curr_ind = 0
    for sent_ind in sent_indss:  # go through all sentences
        while curr_ind < sent_ind:  # iterate through current sentence
            curr = pos_data[curr_ind]
            if curr_ind + 1 <= sent_ind:  # count of tag i do not include last word of sentence
                if curr[1] not in result:
                    result[curr[1]] = 1
                else:
                    result[curr[1]] += 1
            curr_ind += 1
    return result

def generate_emission(pos_data, sent_inds):
    """
    Helper function to generate emission tables.
    """
    c = Counter(pos_data)
    result = {}
    counts = generate_total_count(pos_data, sent_inds)
    for pair in pos_data:
        # pair in format (word, tag)
        word, tag = pair
        if tag in UNIVERSAL_TAGS:
            # the key
            curr_pair = (tag, word)
            if curr_pair not in result:
                # count of word appearance
                count = c[pair]
                # count of total tag appearance, including the tail
                total_count = counts[tag]
                # get the value
                result[curr_pair] = np.log(count/total_count)
    return result


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