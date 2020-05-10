import pytest

from l3.core import dice


class TestConstantOffset:
    def test_roll_does_not_crash(self):
        d = dice.ConstantOffset(5)
        d.roll()

    def test_constant_offset_returns_value_passed_to_constructor(self):
        initial_value = 93
        d = dice.ConstantOffset(initial_value)
        assert d.value == initial_value

    def test_roll_does_not_change_value(self):
        initial_value = 27
        d = dice.ConstantOffset(initial_value)
        d.roll()
        assert d.value == initial_value

    def test_num_sides_returns_value(self):
        initial_value = 13
        d = dice.ConstantOffset(initial_value)
        assert d.num_sides == initial_value


# The upper bound of the ranges in the following methods is arbitrary, but
# it has to be high enough that the the possibility of not generating all
# values with that many iterations is essentially 0 and low enough that the
# test fails within a reasonable time if it catches an implementation error.


@pytest.mark.skip
def _test_init_generates_all_valid_values(constructor,
                                          expected_num_initial_values):
    generated_initial_values = set()
    for _ in range(1_000_000):
        d = constructor()
        generated_initial_values.add(d.value)
        if len(generated_initial_values) == expected_num_initial_values:
            break
    assert len(generated_initial_values) == expected_num_initial_values


@pytest.mark.skip
def _test_roll_generates_all_valid_values(constructor,
                                          expected_num_rolled_values):
    d = constructor()
    rolled_values = set()
    for _ in range(1_000_000):
        d.roll()
        rolled_values.add(d.value)
        if len(rolled_values) == expected_num_rolled_values:
            break
    assert len(rolled_values) == expected_num_rolled_values


class TestRegularDie:
    @pytest.mark.parametrize('num_sides', [-1, 0, 1])
    def test_init_fails_for_invalid_argument(self, num_sides):
        with pytest.raises(ValueError):
            dice.RegularDie(num_sides)

    def test_init_succeeds_for_two_sided_die(self):
        assert isinstance(dice.RegularDie(2), dice.RegularDie)

    def test_init_generates_all_valid_values(self):
        num_sides = 8
        _test_init_generates_all_valid_values(
            lambda: dice.RegularDie(num_sides),
            num_sides
        )

    @pytest.mark.parametrize('num_sides', [2, 6, 31])
    def test_num_sides_returns_correct_value(self, num_sides):
        d = dice.RegularDie(num_sides)
        assert d.num_sides == num_sides

    def test_roll_generates_all_valid_values(self):
        num_sides = 12
        _test_roll_generates_all_valid_values(
            lambda: dice.RegularDie(num_sides),
            num_sides
        )

    @pytest.mark.parametrize('value', range(1, 7))
    def test_value_setter_sets_value_for_valid_input(self, value):
        d = dice.RegularDie()
        d.value = value
        assert d.value == value

    @pytest.mark.parametrize('value', [-3, 0, 7])
    def test_value_setter_throws_for_invalid_input(self, value):
        d = dice.RegularDie()
        with pytest.raises(ValueError):
            d.value = value


class TestPairOfDice:
    def test_init_generates_all_valid_values(self):
        _test_init_generates_all_valid_values(
            lambda: dice.PairOfDice(),
            11  # Valid results are numbers between 2 and 12
        )

    def test_roll_generates_all_valid_values(self):
        _test_roll_generates_all_valid_values(
            lambda: dice.PairOfDice(),
            11  # Valid results are numbers between 2 and 12
        )

    def test_values_getter_and_setter(self):
        d = dice.PairOfDice()
        d.values = 3, 4
        assert d.values == (3, 4)

    @pytest.mark.parametrize('value', range(1, 7))
    def test_is_double_returns_true_for_doubles(self, value):
        d = dice.PairOfDice()
        d.values = (value, value)
        assert d.is_double

    @pytest.mark.parametrize('value', [1, 2, 4, 5, 6])
    def test_is_double_returns_false_when_values_are_different(self, value):
        d = dice.PairOfDice()
        d.values = (3, value)
        assert not d.is_double


# noinspection PyPep8Naming
class TestRpgDice:
    from l3.core.dice import RegularDie as D
    from l3.core.dice import ConstantOffset as C

    @pytest.mark.parametrize('conf,expected', [('1d6', (1, D, 6)),
                                               ('3d8', (3, D, 8)),
                                               ('5D4', (5, D, 4)),
                                               ('d6', (1, D, 6)),
                                               ('D8', (1, D, 8)),
                                               ('2', (1, C, 2))])
    def test_parse_single_die_configuration_returns_correct_spec(
            self, conf, expected):
        actual_dies = dice.RpgDice.parse_single_die_configuration(conf)
        assert len(actual_dies) == len(expected)
        for die, exp in zip(actual_dies, expected):
            assert die == exp

    @pytest.mark.parametrize(
        'conf,expected',
        [('1d6', [(1, D, 6)]),
         ('d6 + 3', [(1, D, 6), (1, C, 3)]),
         ('2d6 + 3d4 + 5', [(2, D, 6), (3, D, 4), (1, C, 5)])])
    def test_parse_configuration_returns_correct_dice(self, conf, expected):
        actual_dice = dice.RpgDice.parse_configuration(conf)
        assert len(actual_dice) == len(expected)
        for die, exp in zip(actual_dice, expected):
            assert die == exp

    @pytest.mark.parametrize(
        'spec,expected',
        [((1, D, 6), [D(6)]),
         ((3, D, 8), [D(8), D(8), D(8)]),
         ((1, C, 5), [C(5)])]
    )
    def test_dice_from_single_spec(self, spec, expected):
        actual_dice = dice.RpgDice.dice_from_single_spec(spec)
        assert len(actual_dice) == len(expected)
        for die, exp in zip(actual_dice, expected):
            assert type(die) == type(exp)
            assert die.num_sides == exp.num_sides

    @pytest.mark.parametrize(
        'specs,expected',
        [([(1, D, 6)], [D(6)]),
         ([(3, D, 8)], [D(8), D(8), D(8)]),
         ([(1, C, 5)], [C(5)]),
         ([(1, D, 3), (2, D, 8), (1, C, 3)], [D(3), D(8), D(8), C(3)])]
    )
    def test_dice_from_specs(self, specs, expected):
        actual_dice = dice.RpgDice.dice_from_specs(specs)
        assert len(actual_dice) == len(expected)
        for die, exp in zip(actual_dice, expected):
            assert type(die) == type(exp)
            assert die.num_sides == exp.num_sides
