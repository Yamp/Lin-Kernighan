from functools import lru_cache

import numpy as np
import numba as nb

from lin_kernighan.algorithms.utils.utils import rotate_zero


@lru_cache
def generate_degrees(number: int, module: int, size: int) -> np.ndarray:
    """ Вычисление степеней 0 - size числа number по модулю module
    number: чьи степени ищем
    module: по какому модулю
    size: сколько степеней
    return: [1, number, number^2 % module ... number^(size -1)]
    """
    nums = np.zeros(size, dtype=np.int64)
    nums[0], nums[1] = 1, number
    for i in range(1, size):
        number = (number * number) % module
        nums[i] = number
    return nums


def generate_hash_from(tour: np.ndarray, number: int, module: int) -> int:
    """ Вычисление хеша для тура по туру и списку степенй
    tour: список городов
    number: чьи степени ищем
    return: хеш
    """
    degrees = generate_degrees(number, module, len(tour))
    return (tour * degrees % module).sum() % module


@nb.njit
def generate_hash(tour: np.ndarray, number=333667, module=909090909090909091) -> int:
    """ Вычисления  хеша по туру
    tour: список вершин
    number: чьи степени будем искать
    module: по какому модулю
    return: хеш
    """
    with nb.objmode(h='int64'):
        h = generate_hash_from(rotate_zero(tour), number, module)
    return h
