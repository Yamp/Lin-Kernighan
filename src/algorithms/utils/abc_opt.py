import logging
from abc import ABC, abstractmethod
from typing import Set

import numpy as np

from src.algorithms.structures.collector import Collector
from src.algorithms.structures.tabu_list import TabuSet
from src.algorithms.utils.hash import generate_hash
from src.algorithms.utils.utils import get_length


class AbcOpt(ABC):
    """ Абстрактный класс, описывающий методы локального поиска
    """

    def __init__(self, length: float, tour: np.ndarray, adjacency: np.ndarray, **kwargs):
        """
        length: Текущая длина тура
        tour: Список городов
        adjacency: Матрица весов
        """
        logging.info('initialization')
        self.length, self.tour, self.matrix = length, tour, adjacency
        self.solutions: Set[int] = {generate_hash(self.tour)}
        self.size = len(tour)

        self.tabu_list = None  # проверенные ранее туры
        self.collector = None  # для сбора данных

    @abstractmethod
    def improve(self) -> float:
        """ Локальный поиск (поиск изменения + само изменение)
        return: выигрыш от локального поиска
        """

    def optimize(self) -> np.ndarray:
        """ Запуск локального поиска
        return: новый маршрут
        """
        gain, iteration, self.collector = 1, 0, Collector(['length', 'gain'], {'two_opt': self.size})
        self.collector.update({'length': self.length, 'gain': 0})
        logging.info(f'start : {self.length}')

        while gain > 0:
            gain = self.improve()
            if gain > 0:
                logging.info(f'{iteration} : {self.length}')
                iteration += 1

            h = generate_hash(self.tour)
            if h in self.solutions:
                break
            else:
                self.solutions.add(h)

            assert round(get_length(self.tour, self.matrix), 2) == round(self.length, 2), \
                f'{get_length(self.tour, self.matrix)} != {self.length}'

        return self.tour

    def tabu_optimize(self, tabu_list: TabuSet, collector: Collector) -> np.ndarray:
        """ Запуск локального поиска под управление tabu search
        tabu_list: проверенные ранее маршруты
        collector: структура для сбора данных о локальном поиске
        return: новый маршрут
        """
        self.tabu_list, best_change, self.collector = tabu_list, -1, collector
        self.collector.update({'length': self.length, 'gain': 0})
        logging.info(f'Start: {self.length}')

        while best_change > 0:
            gain = self.improve()
            if gain > 0.0:
                if self.tabu_list.contains(self.tour):
                    break
                self.length -= gain
                tabu_list.append(self.tour, self.length)
                self.collector.update({'length': self.length, 'gain': -best_change})

        logging.info(f'End: {self.length}')
        return self.tour