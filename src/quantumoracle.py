
import os
from typing import List

from matplotlib import pyplot as plt

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate



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
        
        print(oracle)
        
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
    
        from qiskit import transpile
        from qiskit_aer import AerSimulator
        
        qc = QuantumCircuit(3,2)
        qc = qc.compose(self.circuit, [0,1,2])
        
        simulator = AerSimulator()
        transpiled_circuit = transpile(qc, simulator)
        job = simulator.run(transpiled_circuit)
        counts = job.result().get_counts()        
        
        return counts



if __name__ == "__main__":
    
    #%#########################################################################
    # Create and Run a Word(le) Oracle Circuit
    #%#########################################################################
    
    # The solution to the Wordle game
    solution = 'fresh'
    
    # The letter we want to determine the position of
    letter = 'e'
    
    # The index of the letter in our prior guess,
    # for which the letter is known to have been in the incorrect position
    # (ie: the index we are excluding from the search, to get the superposition
    # down to only four options)
    position = 4
    
    # Build and run the circuit
    wordle_builder = SimpleWordleCircuitBuilder(solution, letter, position)
    counts = wordle_builder.run()
    '''
    NOTE: IBM (and subsequently Qiskit) uses a reverse notation for bit ordering
    
    In the counts dictionary
        qubit q_0 is the LAST bit in the key string,
        qubit q_1 is second to last,
        ...
        qubit q_n is the FIRST bit in the key string
    
    So, we will likely want to take the reverse of the key strings for
    processing the results
    '''
    
    # Print the results
    print(wordle_builder.circuit)
    
    wordle_builder.circuit.draw(output='mpl', filename='circuit', initial_state=True)
    
    print(counts)
    
    
    
    
    
    
    
    
    
    
    