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


    #init prior
    prior = []
    for i in range(N_tags):
        prior.append(0)


    #first lets get all the sentences out
    extractedSentences = []
    for i in range(len(sent_inds)):
        if (i == len(sent_inds)-1):
            last = sent_inds[i]
            extractedSentences.append(pos_data[last:])
        else:
            start = sent_inds[i]
            end = sent_inds[i+1]
            extractedSentences.append(pos_data[start:end])


    #now lets calc the log probabilities for beginning of sequence (first word of out sentences)
    for line in extractedSentences:
        firstWord = line[0]
        firstTag = firstWord[1]
        for i in range(N_tags):
            if firstTag == UNIVERSAL_TAGS[i]:
                prior[i] += 1


    prior = np.log(np.array(prior)/len(extractedSentences))


    #init transition table now
    transition = np.zeros((N_tags, N_tags))

    for line in extractedSentences:
        lineSize = len(line)
        for wordInd in range(lineSize - 1):
            fromWord = line[wordInd]
            toWord = line[wordInd + 1]

            fromTag = fromWord[1]
            toTag = toWord[1]

            fromInd = UNIVERSAL_TAGS.index(fromTag)
            toInd = UNIVERSAL_TAGS.index(toTag)

            transition[fromInd][toInd] += 1

    for rowInd in range(len(transition)):
        row = transition[rowInd]
        div = sum(row)
        for v in range(len(row)):
            transition[rowInd][v] = np.log(transition[rowInd][v]/div)

    #now, onto emission

    emission = {}
    # We need to keep track of how many times each tag appears so we can calc prob of word
    totalPerTag = {}
    for tag in UNIVERSAL_TAGS:
        totalPerTag[tag] = 0

    for line in extractedSentences:
        for wordData in line:
            word = wordData[0]
            wordTag = wordData[1]
            totalPerTag[wordTag] += 1
            pair = (wordTag, word)
            if pair not in emission:
                emission[pair] = 1
            else:
                emission[pair] +=1

    for k, v in emission.items():
        emission[k] = np.log(v/totalPerTag[k[0]])

    ####################

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
    extractedSentences = []
    for i in range(len(sent_inds)):
        if (i == len(sent_inds) - 1):
            last = sent_inds[i]
            extractedSentences.append(pos_data[last:])
        else:
            start = sent_inds[i]
            end = sent_inds[i + 1]
            extractedSentences.append(pos_data[start:end])

    #vit alg
    results = []

    for line in extractedSentences:
        lineLen = len(line)

        prTrel = []
        pathTrel = []
        for i in range(N_tags):
            prTrel.append([])
            pathTrel.append([])

        for i in range(N_tags):
            for j in range(lineLen):
                prTrel[i].append(0)
                pathTrel[i].append(0)


        first = line[0]
        for tagIndex in range(N_tags):
            pair = (UNIVERSAL_TAGS[tagIndex], first)
            prTrel[tagIndex][0] = prior[tagIndex] + emission.get(pair, np.log(0.0000001))
            pathTrel[tagIndex][0] = [tagIndex]

        for others in range(1, lineLen):
            curWord = line[others]

            for tagIndex in range(N_tags):
                pair = (UNIVERSAL_TAGS[tagIndex], curWord)
                recievedPr = emission.get(pair, np.log(0.0000001))

                possibleX = []
                for i in range(len(prTrel)):
                   possibleX.append(prTrel[i][others-1])

                possibleTransitions = []
                for i in range(len(transition)):
                    possibleTransitions.append(transition[i][tagIndex])

                for i in range(len(possibleX)):
                    possibleX[i] += possibleTransitions[i]

                xInd = np.argmax(np.array(possibleX))

                prTrel[tagIndex][others] = possibleX[xInd] + recievedPr
                pathTrel[tagIndex][others] = pathTrel[xInd][others-1] + [tagIndex]

        finalProbs = []
        for i in range(len(prTrel)):
            finalProbs.append(prTrel[i][lineLen-1])

        pathInd = np.argmax(finalProbs)
        finalPath = pathTrel[pathInd][lineLen-1]

        for tagIndex in finalPath:
            results.append(UNIVERSAL_TAGS[tagIndex])

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


