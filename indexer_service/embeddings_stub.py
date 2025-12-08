import numpy as np
from config import VECTOR_DIM

def generate_vector():
    """Имитация работы embedder-а."""
    return np.random.rand(VECTOR_DIM).tolist()

