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

# Get the index for each tag
TAG_INDICIES = {k: v for v, k in enumerate(UNIVERSAL_TAGS)}


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
    # Format the file name to avoid errors
    pos_data = read_data_train(f'{train_file_name}.txt')
    sent_inds = read_data_ind(f'{train_file_name}.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    # Keep track of the number of times tag1 preceeds anything, not just tag2
    count_precedes = Counter()
    # Initialize the 2D-array to store transition probabilities
    transition = np.zeros((N_tags, N_tags))

    # Keep track that the first word in a sentence doesn't have a preceding word
    no_preceding = False

    count_emissions = []  # Keep track of the emissions for each UNIVERSAL_TAG
    for _ in range(N_tags):
        count_emissions.append({})
    count_prior = Counter()  # Keep track of the prior counts to use in prior

    sent_inds2 = sent_inds.copy()
    # Appending the final index of pos in order to loop sentences from start to end index
    sent_inds2.append(len(pos_data))

    # Loop over all the sentences and populate relevant counts
    for i in range(len(sent_inds)):
        curr_index = sent_inds[i]

        # Index 1 in the tuples holds the tag assoc with the word
        curr_tag = pos_data[curr_index][1]
        count_prior[curr_tag] += 1

        no_preceding = True  # First word in a sentence has no preceding so initially set to True

        # Loop from the start of a sentence to the end using the new list of indicies
        for k in range(sent_inds2[i], sent_inds2[i + 1]):
            curr_word = pos_data[k][0]
            curr_index = TAG_INDICIES[pos_data[k][1]]

            # Add a 0 to emission counts if the word doesn't exist instead of None to prevent a TypeError
            count_emissions[curr_index][curr_word] = count_emissions[curr_index].get(
                curr_word, 0) + 1

            if not no_preceding:  # Not first word, so a preceding word exists
                # Where pos_data[k - 1][1] is the previous tag
                count_precedes[pos_data[k - 1][1]] += 1
                prev_index = TAG_INDICIES[pos_data[k - 1][1]]

                # The transition array increments counts for the current tag given the previous tag
                transition[prev_index, curr_index] += 1
            else:
                no_preceding = False  # The next word onwards will have a preceding word

    emission, prior, precedes_anything = {}, [0] * N_tags, [0] * N_tags

    for i in range(N_tags):
        # The denom for each emission probability
        count_word_given_tag = sum(count_emissions[i].values())

        # Prior = the counts for the tag  div by the total number of words
        precedes_anything[i] = count_precedes[UNIVERSAL_TAGS[i]]
        prior[i] = count_prior[UNIVERSAL_TAGS[i]] / len(sent_inds)

        for w, count_w in count_emissions[i].items():
            # Emission at (tag, word) is the number of times the word appears div by the number of times the tag appears for it
            emission[(UNIVERSAL_TAGS[i], w)] = np.log(
                count_w / count_word_given_tag)

    # Number of times tag1 precedes tag2 div by the number of times tag1 precedes anything: P(A|B) = count(A, B) / count(B).
    transition_transposed = transition.T 
    final_transition = transition_transposed / precedes_anything
    final_transition_transposed = np.log(final_transition).T
    return np.log(prior), final_transition_transposed, emission


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
    # COMMENTED OUT LINE BELOW
    #write_results(test_file_name+'.pred', results)


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
