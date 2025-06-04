import numpy as np
import signal
import time
import sys
import os

from tagger import tag as mytag
from tagger import train_HMM
from collections import defaultdict

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

class TimeOutException(Exception):
    pass

class NotEqual(Exception):
    pass

def alarm_handler(signum, frame):
    raise TimeOutException()

def read_data_test(path):
    return open(path, 'r').read().split('\n')

def test_tagging(test_file):

	solution_file = "/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/"+test_file+'.soln'
	pred = np.asarray(read_data_test(test_file+'.pred'))
	soln = np.asarray(read_data_test(solution_file)[:-1])

	acc = np.sum(pred==soln) / len(soln)
	#f = open(fname, "a")
	#f.write("{}, {}\n".format(name, round(acc*100,0)))
	#f.close()
	pct = min(acc, tagging_threshold) / tagging_threshold
	acc = round(acc * 100, 0)
	print("done.")

	return pct, acc

def almost_equal(a, b, diff=1e-4):
	if a == -np.inf:
		return b == -np.inf
	return np.abs(a-b) < diff

def array_almost_equal(a, b, diff=1e-4):
	if a.shape != b.shape:
		raise NotEqual()
		#return False
	a_flat = a.flatten()
	b_flat = b.flatten()
	for i in range(a_flat.shape[0]):
		if not almost_equal(a_flat[i], b_flat[i]):
			raise NotEqual()
			#return False
	return True

scheme = {
	'prior_a': 7,
	'prior_b': 7,
	'transition_a':7,
	'transition_b':7,
	'emission_a':7,
	'emission_b':7,
	'tagging_small':35,
	'tagging_large':23
}

tagging_threshold = 0.85

test_names = list(scheme.keys())

if __name__ == '__main__':

	name = sys.argv[1]
	fname = sys.argv[2]
	gname = name + "_results.txt"

	results = defaultdict(float)
	solutions = np.load('/Users/JaglalLab/Desktop/csc384-a3/ta/soln/soln-private-1.npz')
	signal.signal(signal.SIGALRM, alarm_handler)
	g = open(gname, "w")
	deduction = 0

	signal.alarm(60)
	prior, transition, emission = None, None, None
	with np.errstate(divide='warn'):
		try:
			prior, transition, emission = train_HMM('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/train-private-1')
		except TimeOutException as ex:
			g.write("TimeOutException when training. {}\n".format(ex))
		except Exception as e:
			g.write("Exception when training. {}\n".format(e))

	signal.alarm(60)
	with np.errstate(divide='raise'):
		try:
			prior, transition, emission = train_HMM('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/train-private-1')
		except TimeOutException as ex:
			g.write("TimeOutException when training. {}\n".format(ex))
		except Exception as e:
			g.write("Exception when training. {}\n".format(e.args))
			deduction += 5

	signal.alarm(60)
	prior_2, transition_2, emission_2 = None, None, None
	with np.errstate(divide='warn'):
		try:
			prior_2, transition_2, emission_2 = train_HMM('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/train-private-1')
		except TimeOutException as ex:
			g.write("TimeOutException when training. {}\n".format(ex))
		except Exception as e:
			g.write("Exception when training. {}\n".format(e))

	# Prior Tests
	signal.alarm(60)
	try:
		assert(array_almost_equal(prior, solutions['prior']))
		results['prior_a'] = scheme['prior_a']
	except TimeOutException as ex:
		g.write("TimeOutException when testing prior. {}\n".format(ex))
	except NotEqual:
		g.write("Values in prior are not all equal to solution.\n")
	except Exception as e:
		g.write("Exception when testing prior.\n")

	signal.alarm(60)
	try:
		assert(almost_equal(np.sum(np.exp(prior_2)), 1))
		results['prior_b'] = scheme['prior_b']
	except TimeOutException as ex:
		g.write("TimeOutException when testing prior. {}\n".format(ex))
	except NotEqual:
		g.write("Values in prior are not all equal to solution.\n")
	except Exception as e:
		g.write("Exception when testing prior.\n")

	# Transition Tests
	signal.alarm(60)
	try:
		assert(array_almost_equal(transition, solutions['transition']))
		results['transition_a'] = scheme['transition_a']
	except TimeOutException as ex:
		g.write("TimeOutException when testing transition. {}\n".format(ex))
	except NotEqual:
		g.write("Values in transition are not all equal to solution.\n")
	except Exception as e:
		g.write("Exception when testing transition. {}\n".format(e))

	signal.alarm(60)
	try:
		assert(array_almost_equal(np.sum(np.exp(transition), axis=1), np.ones(N_tags)))
		results['transition_b'] = scheme['transition_b']
	except TimeOutException as ex:
		g.write("TimeOutException when testing transition. {}\n".format(ex))
	except NotEqual:
		g.write("Values in transition are not all equal to solution.\n")
	except Exception as e:
		g.write("Exception when testing transition. {}\n".format(e))

	# Emission Tests
	signal.alarm(60)
	try:
		assert(array_almost_equal(np.asarray([emission[(key[0], key[1])] for key in solutions['emission_key']]), solutions['emission_val']))
		results['emission_a'] = scheme['emission_a']
	except TimeOutException as ex:
		g.write("TimeOutException when testing emission. {}\n".format(ex))
	except NotEqual:
		g.write("Values in emission are not all equal to solution.\n")
	except Exception as e:
		g.write("Exception when testing emission. {}\n".format(e))

	signal.alarm(60)
	try:
		for tag in UNIVERSAL_TAGS:
			assert(almost_equal(np.sum(np.exp([emission_2[key] for key in emission_2 if key[0]==tag])), 1))
		results['emission_b'] = scheme['emission_b']
	except TimeOutException as ex:
		g.write("TimeOutException when testing emission. {}\n".format(ex))
	except NotEqual:
		g.write("Values in emission are not all equal to solution.\n")
	except Exception as e:
		g.write("Exception when testing emission. {}\n".format(e))

	# Tagging tests
	signal.alarm(60)
	acc1, acc2 = 0, 0
	# Small
	with np.errstate(divide='raise'):
		try:
			cmd = "python3 tagger.py -d train-private-1 -t test-private-small-1"
			os.system(cmd)
			results['tagging_small'], acc1 = test_tagging('test-private-small-1')
			results['tagging_small'] = results['tagging_small']*scheme['tagging_small']
		except TimeOutException as ex:
			g.write("TimeOutException when tagging small corpus. {}\n".format(ex))
		except Exception as e:
			g.write("Exception when tagging small corpus. {}\n".format(e.args))

	signal.alarm(120)
	# Large
	with np.errstate(divide='raise'):
		try:
			cmd = "python3 tagger.py -d train-private-1 -t test-private-large-1"
			os.system(cmd)
			results['tagging_large'], acc2 = test_tagging('test-private-large-1')
			results['tagging_large'] = results['tagging_large']*scheme['tagging_large']
		except TimeOutException as ex:
			g.write("TimeOutException when tagging large corpus. {}\n".format(ex))
		except Exception as e:
			g.write("Exception when tagging large corpus. {}\n".format(e.args))

	signal.alarm(0)

	res = []
	for t in test_names:
		#print(t+": %.1f/%.1f" % (results[t], scheme[t]))
		res.append(results[t])
	#print("[Total]: %.1f/%.1f" % (np.sum([results[t] for t in test_names]), np.sum([scheme[t] for t in test_names])))

	res.append(deduction)
	res.append(acc1)
	res.append(acc2)
	res = ",".join([str(i) for i in res])
	f = open(fname, "a")
	f.write("{}, {}\n".format(name, res))
	f.close()

	print("{}, {}\n".format(name, res))
