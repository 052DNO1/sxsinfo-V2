import pytest
from apps.core.utils import (
    generate_uuid, generate_code, md5_hash,
    parse_date_range, format_datetime, format_date,
    chunks, flatten_dict
)
from datetime import datetime, date
from django.utils import timezone


class TestGenerateUuid:
    def test_returns_string_without_hyphens(self):
        result = generate_uuid()
        assert isinstance(result, str)
        assert '-' not in result

    def test_length_is_32(self):
        result = generate_uuid()
        assert len(result) == 32

    def test_unique_on_multiple_calls(self):
        results = {generate_uuid() for _ in range(100)}
        assert len(results) == 100

    def test_hex_characters_only(self):
        result = generate_uuid()
        assert all(c in '0123456789abcdef' for c in result)


class TestGenerateCode:
    def test_default_length(self):
        result = generate_code()
        assert len(result) == 8

    def test_custom_length(self):
        result = generate_code(length=12)
        assert len(result) == 12

    def test_with_prefix(self):
        result = generate_code(prefix='LAB_')
        assert result.startswith('LAB_')
        assert len(result) == 12

    def test_empty_prefix(self):
        result = generate_code(prefix='')
        assert len(result) == 8

    def test_uppercase_and_digits_only(self):
        chars = set()
        for _ in range(200):
            code = generate_code()
            chars.update(code)
        assert chars.issubset(set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))

    def test_length_zero(self):
        result = generate_code(length=0)
        assert result == ''

    def test_prefix_only(self):
        result = generate_code(prefix='P_', length=0)
        assert result == 'P_'


class TestMd5Hash:
    def test_returns_32_char_hex(self):
        result = md5_hash('test')
        assert len(result) == 32
        assert all(c in '0123456789abcdef' for c in result)

    def test_deterministic(self):
        assert md5_hash('hello') == md5_hash('hello')

    def test_different_inputs_different_hashes(self):
        assert md5_hash('a') != md5_hash('b')

    def test_empty_string(self):
        result = md5_hash('')
        assert isinstance(result, str)
        assert len(result) == 32

    def test_unicode_input(self):
        result = md5_hash('中文测试')
        assert isinstance(result, str)
        assert len(result) == 32


class TestParseDateRange:
    def test_single_range(self):
        assert parse_date_range('1-4') == [1, 2, 3, 4]

    def test_comma_separated(self):
        assert parse_date_range('1,3,5') == [1, 3, 5]

    def test_mixed_range_and_comma(self):
        assert parse_date_range('1-4,6,8-10') == [1, 2, 3, 4, 6, 8, 9, 10]

    def test_single_value(self):
        assert parse_date_range('5') == [5]

    def test_duplicate_values_deduplicated(self):
        assert parse_date_range('1-3,2,3') == [1, 2, 3]

    def test_result_sorted(self):
        assert parse_date_range('5,1,3') == [1, 3, 5]

    def test_range_with_spaces(self):
        assert parse_date_range('1 - 4') == [1, 2, 3, 4]

    def test_comma_with_spaces(self):
        assert parse_date_range('1 , 3 , 5') == [1, 3, 5]

    def test_empty_string(self):
        assert parse_date_range('') == []

    def test_empty_parts(self):
        assert parse_date_range('1,,3') == [1, 3]

    def test_non_numeric_ignored(self):
        assert parse_date_range('abc') == []

    def test_mixed_valid_invalid(self):
        assert parse_date_range('1-3,abc,5') == [1, 2, 3, 5]

    def test_range_same_start_end(self):
        assert parse_date_range('3-3') == [3]

    def test_typical_time_slot(self):
        assert parse_date_range('1-2') == [1, 2]

    def test_typical_weeks(self):
        result = parse_date_range('1-18')
        assert result == list(range(1, 19))

    def test_odd_weeks(self):
        assert parse_date_range('1,3,5,7,9,11,13,15,17') == [1, 3, 5, 7, 9, 11, 13, 15, 17]

    def test_complex_weeks(self):
        assert parse_date_range('1-4,6,8-10') == [1, 2, 3, 4, 6, 8, 9, 10]


class TestFormatDatetime:
    def test_valid_datetime(self):
        dt = timezone.make_aware(datetime(2025, 6, 15, 10, 30, 45))
        assert format_datetime(dt) == '2025-06-15 10:30:45'

    def test_none_returns_empty(self):
        assert format_datetime(None) == ''

    def test_custom_format(self):
        dt = timezone.make_aware(datetime(2025, 6, 15, 10, 30, 45))
        assert format_datetime(dt, '%Y/%m/%d') == '2025/06/15'


class TestFormatDate:
    def test_valid_date(self):
        d = date(2025, 6, 15)
        assert format_date(d) == '2025-06-15'

    def test_none_returns_empty(self):
        assert format_date(None) == ''

    def test_custom_format(self):
        d = date(2025, 6, 15)
        assert format_date(d, '%Y/%m/%d') == '2025/06/15'


class TestChunks:
    def test_even_split(self):
        result = chunks([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_uneven_split(self):
        result = chunks([1, 2, 3, 4, 5], 2)
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunk_size_larger_than_list(self):
        result = chunks([1, 2], 5)
        assert result == [[1, 2]]

    def test_empty_list(self):
        result = chunks([], 3)
        assert result == []

    def test_chunk_size_one(self):
        result = chunks([1, 2, 3], 1)
        assert result == [[1], [2], [3]]


class TestFlattenDict:
    def test_flat_dict(self):
        result = flatten_dict({'a': 1, 'b': 2})
        assert result == {'a': 1, 'b': 2}

    def test_nested_dict(self):
        result = flatten_dict({'a': {'b': 1, 'c': 2}})
        assert result == {'a.b': 1, 'a.c': 2}

    def test_deeply_nested(self):
        result = flatten_dict({'a': {'b': {'c': 1}}})
        assert result == {'a.b.c': 1}

    def test_custom_separator(self):
        result = flatten_dict({'a': {'b': 1}}, sep='_')
        assert result == {'a_b': 1}

    def test_mixed_types(self):
        result = flatten_dict({'a': 1, 'b': {'c': 'hello'}, 'd': [1, 2]})
        assert result == {'a': 1, 'b.c': 'hello', 'd': [1, 2]}

    def test_empty_dict(self):
        assert flatten_dict({}) == {}

    def test_parent_key(self):
        result = flatten_dict({'b': 1}, parent_key='a')
        assert result == {'a.b': 1}
