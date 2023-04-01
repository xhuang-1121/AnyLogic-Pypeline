from py4j.java_gateway import JavaGateway, CallbackServerParameters
from solver import FacilityOrderSolver
import random
import time

random.seed(1)

class PySolver:
    ''' A wrapper for Py4J '''

    class Java:
        ''' Required by Py4J '''
        implements = ["benchmark___traveling_salesman.ISolver"]

    def __init__(self):
        self.solver = None
        self.gateway = None

    def toString(self):
        ''' Required by Py4J '''
        return "PySolver"

    def setup(self, distance_matrix_2d, home_index):
        start = time.time()
        # input is a pseudo-Java array; need to convert to Python array
        height, width = len(distance_matrix_2d), len(distance_matrix_2d[0])
        matrix = []
        for row_index in range(height):
            row = [distance_matrix_2d[row_index][col_index] for col_index in range(width)]
            matrix.append(row)
        self.solver = FacilityOrderSolver(matrix, home_index)
##        print(f"setup: {time.time()-start}")

    def build_random_order(self, n_select):
        start = time.time()

        num_hubs = len(self.solver.matrix)
        home_index = self.solver.home_index

        order = sorted(
            random.sample(set(range(num_hubs)) - {home_index}, n_select)
            + [home_index]
        )

        # cannot be a Python list; required to return a Java array
        _list = self.gateway.new_array(self.gateway.jvm.int, len(order))

        # like a Java array, need to assign w/indices; no Pythonic way
        for i, v in enumerate(order):
            _list[i] = v

##        print(f"build_random_order(x{n_select}): {time.time()-start}")
        return _list
    

    def get_optimized_order(self, indices_to_visit):
        start = time.time()

        indices_to_visit_converted = list(indices_to_visit)
        solution = self.solver.solve(indices_to_visit_converted)['order']

        # returned output cannot be a Python list; required to return a Java array
        java_list = self.gateway.new_array(self.gateway.jvm.int, len(solution))
        for i, v in enumerate(solution):
            java_list[i] = v

##        print(f"get_optimized_order(x{len(indices_to_visit)}): {time.time()-start}")
        return java_list


if __name__ == "__main__":
    solver = PySolver()
    gateway = JavaGateway(
        callback_server_parameters=CallbackServerParameters(),
        python_server_entry_point=solver)
    # Implement hacky workaround
    solver.gateway = gateway
    print("Gateway active")

