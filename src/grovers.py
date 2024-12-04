from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute
from qiskit_aer import Aer
from qiskit.circuit.library import GroverOperator
from qiskit.algorithms import AmplificationProblem, Grover
import numpy as np
import math

class QuantumWordleSolver:
    def __init__(self, word_list, sequential=True):
        """
        Initialize quantum solver with choice of sequential (letter-by-letter) 
        or parallel (whole word) search
        """
        self.word_list = list(word_list)  # Convert set to list for indexing
        self.possible_words = set(word_list)
        self.feedback_history = []
        self.sequential = sequential
        
        # Calculate required qubits
        if sequential:
            self.n_qubits = math.ceil(math.log2(26))  # For individual letters
        else:
            self.n_qubits = math.ceil(math.log2(len(self.word_list)))
            
        # Initialize quantum backend
        self.backend = Aer.get_backend('qasm_simulator')
        
    def _create_letter_oracle(self, feedback_data):
        """Create oracle circuit for finding a specific letter position"""
        def oracle_function(x):
            # Convert binary string to letter
            letter = chr(ord('a') + x)
            
            # Check if letter satisfies all feedback constraints
            for word, feedback in self.feedback_history:
                if not self._letter_matches_feedback(letter, word, feedback):
                    return False
            return True
            
        return oracle_function
        
    def _letter_matches_feedback(self, letter, word, feedback):
        """Check if a letter satisfies the feedback constraints"""
        for i, (guess_letter, result) in enumerate(zip(word, feedback)):
            if result == 'correct' and letter == guess_letter:
                return True
            elif result == 'absent' and letter == guess_letter:
                return False
        return True
        
    def _create_word_oracle(self, feedback_data):
        """Create oracle circuit for finding whole words"""
        def oracle_function(x):
            # Convert index to word
            if x >= len(self.word_list):
                return False
            word = self.word_list[x]
            
            # Check if word satisfies all feedback constraints
            for guess, feedback in self.feedback_history:
                if not self._matches_feedback(word, guess, feedback):
                    return False
            return True
            
        return oracle_function
        
    def _matches_feedback(self, candidate, guess, feedback):
        """Check if a word matches the given feedback pattern"""
        for i, (letter, result) in enumerate(zip(guess, feedback)):
            if result == 'correct' and candidate[i] != letter:
                return False
            elif result == 'absent' and letter in candidate:
                return False
            elif result == 'present' and (letter not in candidate or candidate[i] == letter):
                return False
        return True
        
    def _quantum_search(self, oracle, n_iterations=None):
        """Execute Grover's search with given oracle"""
        # Create amplitude amplification problem
        problem = AmplificationProblem(
            oracle=oracle,
            is_good_state=oracle
        )
        
        # Calculate optimal number of iterations if not specified
        if n_iterations is None:
            n_iterations = int(math.pi/4 * math.sqrt(2**self.n_qubits))
            
        # Create and configure Grover's algorithm
        grover = Grover(
            quantum_instance=self.backend,
            iterations=n_iterations
        )
        
        # Execute search
        result = grover.amplify(problem)
        
        return int(result.top_measurement, 2)
        
    def update_possibilities(self, guess, feedback):
        """Update solver state with new feedback"""
        self.feedback_history.append((guess, feedback))
        
        # Update possible words based on feedback
        new_possibilities = set()
        for word in self.possible_words:
            if self._matches_feedback(word, guess, feedback):
                new_possibilities.add(word)
        self.possible_words = new_possibilities
        
    def get_next_guess(self):
        """Get next guess using quantum search"""
        if len(self.possible_words) <= 1:
            return next(iter(self.possible_words))
            
        if self.sequential:
            # Find each letter sequentially
            guess = [''] * 5
            for pos in range(5):
                oracle = self._create_letter_oracle(pos)
                result = self._quantum_search(oracle)
                guess[pos] = chr(ord('a') + result)
            return ''.join(guess)
        else:
            # Search for whole word
            oracle = self._create_word_oracle(self.feedback_history)
            result = self._quantum_search(oracle)
            return self.word_list[result] if result < len(self.word_list) else next(iter(self.possible_words))

# Example usage with your Wordle game
if __name__ == "__main__":
    # Initialize game
    wordle = Wordle("path_to_dictionary.txt")
    game_state = wordle.start_game()
    
    # Initialize quantum solver
    solver = QuantumWordleSolver(wordle.word_list, sequential=True)
    
    # Play game
    solved = False
    while not solved and game_state['attempts'] < 6:
        # Get quantum solver's guess
        guess = solver.get_next_guess()
        
        # Make guess and get feedback
        result = wordle.make_guess(guess)
        
        # Check if solved
        if all(r == 'correct' for r in result['result']):
            solved = True
            print(f"Solved in {game_state['attempts']} attempts!")
            break
            
        # Update solver with feedback
        solver.update_possibilities(guess, result['result'])
        
    if not solved:
        print("Failed to solve!")