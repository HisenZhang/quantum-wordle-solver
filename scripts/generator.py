import itertools
import string
from typing import List
import argparse

def generate_dictionary(length: int, possible_letters: int, size: int = None, allow_repeats: bool = True) -> List[str]:
    """Generate dictionary words based on specified parameters."""
    letters = string.ascii_lowercase[:possible_letters]
    
    if allow_repeats:
        words = itertools.product(letters, repeat=length)
    else:
        if length > len(letters):
            return []
        words = itertools.permutations(letters, length)
    
    result = [''.join(word) for word in words]
    if size:
        result = result[:size]
    return result

def main():
    parser = argparse.ArgumentParser(description='Generate dictionary words')
    parser.add_argument('-l', '--length', type=int, required=True, help='Length of each word')
    parser.add_argument('-a', '--possible_letters', type=int, required=True, choices=range(1, 27), default=26,
                        help='Number of possible letters (1-26)')
    parser.add_argument('-s', '--size', type=int, help='Maximum number of words to generate')
    parser.add_argument('-nr', '--no_repeats', action='store_true', help='Disable repeating letters')
    parser.add_argument('-o', '--output', default='dictionary.txt', help='Output file name')
    args = parser.parse_args()

    words = generate_dictionary(args.length, args.possible_letters, args.size, not args.no_repeats)
    
    with open(args.output, 'w') as f:
        f.write('\n'.join(words))

if __name__ == '__main__':
    main()