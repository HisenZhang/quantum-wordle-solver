from typing import List, Set, Tuple
import numpy as np

import os

from matplotlib import pyplot as plt

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit import transpile
from qiskit_aer import AerSimulator


class SimpleOracleBuilder():

    def __init__(self, id: str, qubit_count: int, solutions: List[int]):
        
        self.ID = id
        self.QUBIT_COUNT = qubit_count
        self.SOLUTIONS = solutions
        
    def build_circuit(self):
        
        def invert_for_control(circuit: QuantumCircuit, solution: str):
            sol_str = bin(solution)[2:].zfill(self.QUBIT_COUNT)
            # Iterate over the bits in the solution
            for req_i in range(len(sol_str)):
                bit_val = int(sol_str[req_i])
                if not bit_val:
                    circuit.x(req_i)
                  
        oracle = QuantumCircuit(self.QUBIT_COUNT+1)
        
        # For each solution, we can just use a bunch of CNOTs to
        # check if an input should result in an output of 1
        for solution in self.SOLUTIONS:
            
            # We may need to invert the qubits to check for zeros
            invert_for_control(oracle, solution)
            
            # Apply the muli-qubit control onto the output qubit
            control = MCXGate(self.QUBIT_COUNT)
            oracle.append(control, range(self.QUBIT_COUNT+1))
            
            # We may need to undo the inversion of qubits to check for zeros
            invert_for_control(oracle, solution)
        
        # print(oracle)
        
        return oracle.to_instruction(label=self.ID)
        


class SimpleWordleCircuitBuilder():
    
    def __init__(self, solution_word: str, checked_letter: str, checked_index: int):
        
        self.SOLUTIONS = []
        self.NON_SOLUTIONS = []
        
        for i in range(len(solution_word)):
            if i != checked_index:
                if solution_word[i] == checked_letter:
                    self.SOLUTIONS.append(i if i < checked_index else i-1)
                else:
                    self.NON_SOLUTIONS.append(i if i < checked_index else i-1)
        
        print(self.SOLUTIONS)
        print(self.NON_SOLUTIONS)
        
        self.circuit = None
        
    def build(self):
        
        qc = QuantumCircuit(3, 2)
        
        # Put qubit 2 in the |-> state for phase gates 
        qc.x(2)
        qc.h(2)
        
        # Create a superposition over the two input qubits
        qc.h([0,1])
        
        # Compose the oracle for Zf and add it to the circuit
        zf_builder = SimpleOracleBuilder('Zf', 2, self.SOLUTIONS)
        qc = qc.compose(zf_builder.build_circuit(), [0,1,2])
        
        # Apply hadamards for the start of the diffusor operation
        qc.h([0,1])
        
        # Create the ZOR gate
        zor_builder = SimpleOracleBuilder('ZOR', 2, [0b01, 0b10, 0b11])
        qc = qc.compose(zor_builder.build_circuit(), [0,1,2])
        
        # Apply hadamards to complete the diffusor operation
        qc.h([0,1])
        
        # Measure
        qc.measure([0,1], [0,1])
        
        self.circuit = qc
        
        return(qc.to_instruction(label='Solver'))
    
    def run(self):
        
        # If the circuit has not been build, then build it
        if self.circuit == None:
            self.build()
    
        qc = QuantumCircuit(3,2)
        qc = qc.compose(self.circuit, [0,1,2])
        
        simulator = AerSimulator()
        transpiled_circuit = transpile(qc, simulator)
        job = simulator.run(transpiled_circuit)
        counts = job.result().get_counts()        
        
        return counts

from typing import List, Set, Tuple
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit import transpile
from qiskit_aer import AerSimulator
import numpy as np

class QuantumWordleSolver:
    def __init__(self, word_list: List[str]):
        self.possible_words = set(word_list)
        self.feedback_history = []
        self.word_length = len(next(iter(word_list)))
        
    def update_possibilities(self, guess: str, feedback: List[str]):
        """Update possible words based on Wordle feedback"""
        new_possibilities = set()
        for word in self.possible_words:
            if self._matches_feedback(word, guess, feedback):
                new_possibilities.add(word)
        self.possible_words = new_possibilities
        self.feedback_history.append((guess, feedback))
        
    def get_next_guess(self) -> str:
        """Use quantum circuit to find optimal next guess"""
        if len(self.possible_words) <= 2:
            return next(iter(self.possible_words))
            
        # Create quantum circuits for each position
        best_scores = []
        for pos in range(self.word_length):
            # Build circuit to evaluate letter positions
            circuit_builder = PositionEvaluationCircuit(
                list(self.possible_words),
                pos
            )
            counts = circuit_builder.run()
            score = self._analyze_measurement_results(counts)
            best_scores.append((score, pos))
            
        # Choose position with highest quantum score
        best_pos = max(best_scores, key=lambda x: x[0])[1]
        
        # Select word that maximizes information gain at that position
        return self._select_word_for_position(best_pos)
    
    def _matches_feedback(self, candidate: str, guess: str, feedback: List[str]) -> bool:
        """Check if a candidate word matches Wordle feedback"""
        for i, (letter, result) in enumerate(zip(guess, feedback)):
            if result == 'correct' and candidate[i] != letter:
                return False
            elif result == 'absent' and letter in candidate:
                return False
            elif result == 'present' and (letter not in candidate or candidate[i] == letter):
                return False
        return True
        
    def _analyze_measurement_results(self, counts: dict) -> float:
        """Analyze quantum measurement results to score position"""
        total_shots = sum(counts.values())
        # Calculate Shannon entropy of measurements
        entropy = 0
        for count in counts.values():
            prob = count / total_shots
            entropy -= prob * np.log2(prob) if prob > 0 else 0
        return entropy
        
    def _select_word_for_position(self, position: int) -> str:
        """Select word that maximizes information gain at given position"""
        best_word = None
        max_score = float('-inf')
        
        for word in self.possible_words:
            # Count unique letters at this position across possible words
            letter_freq = {}
            for possible in self.possible_words:
                letter_freq[possible[position]] = letter_freq.get(possible[position], 0) + 1
                
            # Score based on letter frequency distribution
            score = -sum((freq/len(self.possible_words)) * 
                        np.log2(freq/len(self.possible_words)) 
                        for freq in letter_freq.values())
                        
            if score > max_score:
                max_score = score
                best_word = word
                
        return best_word

class PositionEvaluationCircuit:
    def __init__(self, words: List[str], position: int):
        self.words = words
        self.position = position
        self.qubit_count = len(bin(len(words))[2:])  # Number of qubits needed to represent words
        
    def build(self) -> QuantumCircuit:
        """Build quantum circuit to evaluate letter positions"""
        # Create circuit with enough qubits to represent words plus ancilla
        qc = QuantumCircuit(self.qubit_count + 1, self.qubit_count)
        
        # Create superposition of all possible words
        qc.h(range(self.qubit_count))
        
        # Build oracle for letter position checking
        oracle_builder = SimpleOracleBuilder(
            f'pos_{self.position}',
            self.qubit_count,
            self._get_solutions_for_position()
        )
        qc = qc.compose(oracle_builder.build_circuit(), range(self.qubit_count + 1))
        
        # Apply Grover diffusion operator
        qc.h(range(self.qubit_count))
        qc.x(range(self.qubit_count))
        
        # Multi-controlled phase flip
        control_qubits = list(range(self.qubit_count))
        target_qubit = self.qubit_count
        
        # Use MCX gate for multi-controlled operation
        mcx = MCXGate(num_ctrl_qubits=len(control_qubits))
        qc.append(mcx, control_qubits + [target_qubit])
        
        qc.x(range(self.qubit_count))
        qc.h(range(self.qubit_count))
        
        # Measure
        qc.measure(range(self.qubit_count), range(self.qubit_count))
        
        return qc
        
    def run(self) -> dict:
        """Run the quantum circuit and return measurement results"""
        qc = self.build()
        simulator = AerSimulator()
        transpiled = transpile(qc, simulator)
        job = simulator.run(transpiled, shots=1024)
        return job.result().get_counts()
        
    def _get_solutions_for_position(self) -> List[int]:
        """Get binary solutions for oracle based on letter position"""
        solutions = []
        for i, word in enumerate(self.words):
            # Convert word index to binary for quantum oracle
            solutions.append(i)
        return solutions
    
if __name__ == '__main__':    
    from wordle import Wordle    
        
    game = Wordle('../unique_words.txt')
    solver = QuantumWordleSolver(game.word_list)
    game.start_game()

    while True:
        guess = solver.get_next_guess()
        result = game.make_guess(guess)
        if all(x == 'correct' for x in result['result']):
            break
        solver.update_possibilities(guess, result['result'])
        
    print(game.get_game_state())