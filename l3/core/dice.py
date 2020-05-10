import itertools
import math
import random
import re
from abc import ABC, abstractmethod
from typing import Sequence, Callable, Tuple, List

from l3.core.utils import consume


class Die(ABC):
    @abstractmethod
    def roll(self) -> None:
        """"
        Roll the die and store the value. The rolled value can be accessed by
        the value property.
        """
        pass

    @property
    @abstractmethod
    def value(self) -> int:
        """Return the last value rolled with this die."""
        pass

    @property
    @abstractmethod
    def num_sides(self) -> int:
        """Return the number of sides this die has."""
        pass


class ConstantOffset(Die):
    """A constant offset for a set of dice."""

    def __init__(self, value):
        self._value = value

    def roll(self) -> None:
        pass

    @property
    def value(self) -> int:
        return self._value

    @property
    def num_sides(self) -> int:
        return self._value


class RegularDie(Die):
    """
    A single roll of a fair n-sided die.
    """

    def __init__(self, num_sides: int = 6):
        """
        Initialize a Die.
        :param num_sides: The number of sides of the die.
        """
        if num_sides < 2:
            raise ValueError(f"Cannot create a die with less than 2 sides")
        self._num_sides = num_sides
        self._value = 0
        # Roll the die once to ensure we have a valid value.
        self.roll()

    def roll(self) -> None:
        self._value = random.randint(1, self.num_sides)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        if 1 <= value <= self.num_sides:
            self._value = value
        else:
            raise ValueError(f"{self.num_sides}-sided die cannot have value "
                             f"{value}.")

    @property
    def num_sides(self) -> int:
        return self._num_sides


class PairOfDice:
    """
    A single roll with a pair of 6-sided dice.
    """

    def __init__(self):
        self._dice = (RegularDie(6), RegularDie(6))

    def roll(self) -> None:
        consume(map(lambda d: d.roll(), self._dice))

    @property
    def values(self) -> (int, int):
        return tuple(map(lambda d: d.value, self._dice))

    @values.setter
    def values(self, values):
        d1, d2 = self._dice
        v1, v2 = values
        d1.value = v1
        d2.value = v2

    @property
    def value(self) -> int:
        return sum(self.values)

    @property
    def is_double(self) -> bool:
        return self._dice[0].value == self._dice[1].value


class RpgDice:
    """"
    A single roll with a given configuration of dice.

    Dice configurations are specified in the usual RPG notation:
    - d6, D6, 1d6 or 1D6 represent a single roll of a 6-sided die, i.e., an
      uniformly distributed value between 1 and 6.
    - 2d6 or 2D6 represents a single roll of two 6-sided dice, i.e., a value
      between 2 and 12 distributed so that 2 and 12 have probability 1/36 and
      7 has probability 1/6.
    - In general ndk or nDk with positive integers n and k represents a single
      roll of n k-sided dice.
    - Rolls can be added, e.g., 1d4 + 2d6 represents a single roll of one
      4-sided and two 6-sided dice.
    - A single number represents a fixed value. For example, d6 + 4 represents
      a single roll of  a six-sided die to which 4 is added, i.e., a random
      number uniformly distributed between 6 and 10.
    """

    def __init__(self, configuration):
        self.dice = self.parse_configuration(configuration)

    DICE_REGEX = re.compile(r'^\s*(\d*)\s*([Dd]?)\s*(\d+)\s*$')

    @classmethod
    def parse_single_die_configuration(cls, configuration: str) \
            -> Tuple[int, Callable, int]:
        """
        Parse a single die configuration string into a die spec.

        A die spec is a triple with the elements
        - Number of dice this triple represents
        - Function to construct a single die of this type
        - Value/Number of Sides of the dice
        """
        match = cls.DICE_REGEX.match(configuration)
        num_dice = int(match.group(1) or '1')
        dice_kind = RegularDie if match.group(2) else ConstantOffset
        num_sides = int(match.group(3))
        return num_dice, dice_kind, num_sides

    @staticmethod
    def parse_configuration(configuration: str) \
            -> Sequence[Tuple[int, Callable, int]]:
        """
        Parse a configuration string and return a sequence of dice specs.

        Dice specs are triples with the elements
        - Number of dice this triple represents
        - Function to construct a single die of this type
        - Value/Number of Sides of the dice

        :param configuration: A string in the form '2d6 + 4'
        :return: A sequence of Dice specs
        """
        single_configs = configuration.split('+')
        return list(map(RpgDice.parse_single_die_configuration, single_configs))

    @staticmethod
    def dice_from_single_spec(spec: Tuple[int, Callable, int]) -> List[Die]:
        """
        Create a list of Die instances, given a single die spec.

        :param spec: A die spec in the form returned by parse_configuration
        :return: A list of dice
        """
        num_dice, constructor, num_sides = spec
        return [constructor(num_sides)] * num_dice

    @staticmethod
    def dice_from_specs(specs: Sequence[Tuple[int, Callable, int]]) \
            -> List[Die]:
        """
        Create a list of Die instances given a sequence of die specs.

        :param specs: A list of die specs as returned by parse_configuration
        :return: A list of dice
        """
        ds = map(RpgDice.dice_from_single_spec, specs)
        return [die for dice_list in ds for die in dice_list]
