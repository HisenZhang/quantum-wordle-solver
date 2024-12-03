def has_unique_letters(word):
    """Check if a word has only unique letters."""
    return len(set(word.lower())) == len(word)

def filter_dictionary(input_file, output_file):
    """
    Read words from input file and write only words with unique letters to output file.
    Each word should be on a new line in both files.
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                word = line.strip()
                if has_unique_letters(word):
                    outfile.write(word + '\n')
        print(f"Successfully filtered words to {output_file}")
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    filter_dictionary("dictionary.txt", "unique_words.txt")