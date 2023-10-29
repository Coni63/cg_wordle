import math
import random
import numpy as np
from typing import List
import time
#####
# DEFINITION
# candidate: 
# guess:
# result:
#####
options = np.ones(shape=(26, 6))  # All available letters per position


def is_candidate(candidate: List[int], guess: List[int], result: List[int]):
    unmatched_letters = guess[:]

    for i in range(6):
        letter = guess[i]
        if letter == candidate[i]:
            if result[i] != 3:
                return False
            unmatched_letters.remove(letter)
        elif letter in candidate:
            if result[i] != 2:
                return False
            unmatched_letters.remove(letter)
        else:
            if result[i] != 1:
                return False

    return True


def encode(word: str) -> List[int]:
    # encode a word to a list of integer with the index of the letter
    # faster to compare in the options matrix
    return [ord(c) - 65 for c in word]

def decode(seq: List[int]) -> str:
    # decode a list of int to a word
    return "".join([chr(x + 65) for x in seq])

def is_valid(seq: List[int]) -> bool:
    # check if a word has only valid letters
    for i, idx in enumerate(seq):
        if options[idx, i] == 0:
            return False
    return True

def filter_choices(seq: List[List[int]], guess: List[int], result: List[int]):
    # filter the list to keep only valid words
    ans = []
    for x in seq:
        if not is_valid(x):
            continue
        
        if is_candidate(x, guess, result):
            ans.append(x)
    return ans

def pick_best_choice(seq: List[List[int]]) -> List[int]:
    # pick the best words to reduce the dictionary
    # not implemented
    if len(seq) < 250:
        return make_guess(seq)
    else:
        return best_opener(seq)

def update_options_based_on_results(guess: List[int], results: List[int]):
    # Based on the response, update the options matrix to keep only valid positions
    for i, state in enumerate(results):
        idx = guess[i]
        if state == 1:
            # all index cannot have this letter
            options[idx, :] = False
        elif state == 2:
            # this index cannot have this letter
            options[idx, i] = False
        elif state == 3:
            # for the index i, only this letter is possible as it is the good one
            options[:, i] = False
            options[idx, i] = True





def get_mask(candidate: List[int], guess: List[int]) -> List[int]:
    letter_states = [1 for _ in range(6)]

    unmatched_letters = guess[:]

    for i in range(6):
        if guess[i] == candidate[i]:
            letter_states[i] = 3
            unmatched_letters.remove(guess[i])
        elif guess[i] in candidate:
            letter_states[i] = 2
            unmatched_letters.remove(guess[i])

    return letter_states


def compute_entropy(count_masks):
    total = sum(count_masks)
    entropy = 0.0

    for i in count_masks:
        p = i / total
        entropy -= math.log2(p) * p

    return entropy


def make_guess(words: List[List[int]]):
    max_entropy = -1
    best_guess = [0, 0, 0, 0, 0, 0]

    # remaining_entropy = compute_entropy([1 for a in answer_list])
    # remaining_entropy = math.log(len(words))  # These are equivalent
    n = 12500 // len(words)
    k = min(n, len(words))
    for guess in words:
        bins = {}
        for candidate in random.sample(words, k=k):
            mask = get_mask(candidate, guess)
            m_str = "".join(map(str, mask))
            bins[m_str] = bins.get(m_str, 0) + 1

        # Replace best guess if there's a word with better entropy, but defer
        # to valid answers if they have sufficient entropy
        new_entropy = compute_entropy(bins.values())
        if new_entropy > max_entropy:
            max_entropy = new_entropy
            best_guess = guess

    return best_guess


def best_opener(words: List[List[int]]) -> List[int]:
    c = [[0 for _ in range(26)] for i in range(6)]

    total = len(words)
    for guess in words:
        for i, letter in enumerate(guess):
            c[i][letter] += 1 

    max_entropy = -1
    best_guess = [0, 0, 0, 0, 0, 0]
    for guess in words:
        entropy = 0.0
        for i, letter in enumerate(guess):
            p = c[i][letter] / total
            entropy -= math.log2(p) * p
    
        if entropy > max_entropy:
            max_entropy = entropy
            best_guess = guess
    
    return best_guess


def load_words():
    with open("wordlist.txt", "r") as f:
        words = f.read().splitlines()
    return words

def load_testcases():
    with open("test_cases.txt", "r") as f:
        words = f.read().splitlines()
    return words


def main(words: List[str], answer: str):
    global options

    options = np.ones(shape=(26, 6))  # All available letters per position

    words_encoded = [encode(word) for word in words]
    answer_encoded = encode(answer)

    # print("\nWords remaining:", len(words_encoded), file=sys.stderr)

    guess = None
    for i in range(10):
        if guess is not None:
            states = get_mask(answer_encoded, guess)

        if guess is not None:
            update_options_based_on_results(guess, states)
            words_encoded = filter_choices(words_encoded, guess, states) 
            # print("Words remaining:", len(words_encoded), file=sys.stderr)

        guess = pick_best_choice(words_encoded)

        # print(decode(guess), answer)
        if decode(guess) == answer:
            return i+1
    return 10

if __name__ == "__main__":
    random.seed(42)
    words = load_words()
    # answers = load_testcases()
    answers = random.sample(words, 50)

    start = time.time()
    total_turns = 0
    for answer in answers:
        total_turns += main(words, answer)
    stop = time.time()
    print("\n\nTotal Score:", total_turns)
    print("Time taken:", stop - start)
