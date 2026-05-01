import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from common.validators import (
    validate_phone, validate_id_card,
    validate_password_strength, FileSizeValidator, FileExtensionValidator
)
from unittest.mock import MagicMock


class TestValidatePhone:
    def test_valid_phones(self):
        valid_phones = ['13800138000', '15912345678', '18600001111', '19999999999']
        for phone in valid_phones:
            validate_phone(phone)

    def test_invalid_phone_starts_with_10(self):
        with pytest.raises(DjangoValidationError):
            validate_phone('10012345678')

    def test_invalid_phone_starts_with_12(self):
        with pytest.raises(DjangoValidationError):
            validate_phone('12012345678')

    def test_invalid_phone_too_short(self):
        with pytest.raises(DjangoValidationError):
            validate_phone('1380013800')

    def test_invalid_phone_too_long(self):
        with pytest.raises(DjangoValidationError):
            validate_phone('138001380001')

    def test_invalid_phone_letters(self):
        with pytest.raises(DjangoValidationError):
            validate_phone('1380013800a')

    def test_invalid_phone_empty(self):
        with pytest.raises(DjangoValidationError):
            validate_phone('')

    def test_valid_prefixes(self):
        validate_phone('13800138000')
        validate_phone('15912345678')
        validate_phone('18600001111')
        validate_phone('19999999999')


class TestValidateIdCard:
    def test_valid_id_card(self):
        validate_id_card('110101199001011234')

    def test_valid_id_card_with_x(self):
        validate_id_card('11010119900101123X')

    def test_valid_id_card_with_lowercase_x(self):
        validate_id_card('11010119900101123x')

    def test_invalid_too_short(self):
        with pytest.raises(DjangoValidationError):
            validate_id_card('11010119900101')

    def test_invalid_too_long(self):
        with pytest.raises(DjangoValidationError):
            validate_id_card('1101011990010112345')

    def test_invalid_letters_in_body(self):
        with pytest.raises(DjangoValidationError):
            validate_id_card('11010119900a011234')

    def test_invalid_empty(self):
        with pytest.raises(DjangoValidationError):
            validate_id_card('')


class TestValidatePasswordStrength:
    def test_valid_strong_password(self):
        validate_password_strength('Test@1234')

    def test_too_short(self):
        with pytest.raises(DjangoValidationError):
            validate_password_strength('Te1')

    def test_exactly_8_chars(self):
        validate_password_strength('Test1234')

    def test_no_uppercase(self):
        with pytest.raises(DjangoValidationError):
            validate_password_strength('test1234')

    def test_no_lowercase(self):
        with pytest.raises(DjangoValidationError):
            validate_password_strength('TEST1234')

    def test_no_digit(self):
        with pytest.raises(DjangoValidationError):
            validate_password_strength('TestTest')

    def test_only_letters(self):
        with pytest.raises(DjangoValidationError):
            validate_password_strength('TestTest')

    def test_only_digits(self):
        with pytest.raises(DjangoValidationError):
            validate_password_strength('12345678')


class TestFileSizeValidator:
    def test_default_max_size(self):
        validator = FileSizeValidator()
        assert validator.max_size == 10 * 1024 * 1024

    def test_custom_max_size(self):
        validator = FileSizeValidator(max_size_mb=5)
        assert validator.max_size == 5 * 1024 * 1024

    def test_file_under_limit(self):
        validator = FileSizeValidator(max_size_mb=1)
        mock_file = MagicMock()
        mock_file.size = 500 * 1024
        validator(mock_file)

    def test_file_over_limit(self):
        validator = FileSizeValidator(max_size_mb=1)
        mock_file = MagicMock()
        mock_file.size = 2 * 1024 * 1024
        with pytest.raises(DjangoValidationError):
            validator(mock_file)

    def test_file_at_exact_limit(self):
        validator = FileSizeValidator(max_size_mb=1)
        mock_file = MagicMock()
        mock_file.size = 1 * 1024 * 1024
        validator(mock_file)


class TestFileExtensionValidator:
    def test_default_allowed_extensions(self):
        validator = FileExtensionValidator()
        assert 'jpg' in validator.allowed_extensions
        assert 'pdf' in validator.allowed_extensions
        assert 'xlsx' in validator.allowed_extensions

    def test_custom_extensions(self):
        validator = FileExtensionValidator(allowed_extensions=['csv', 'txt'])
        assert validator.allowed_extensions == ['csv', 'txt']

    def test_allowed_extension(self):
        validator = FileExtensionValidator()
        mock_file = MagicMock()
        mock_file.name = 'test.pdf'
        validator(mock_file)

    def test_disallowed_extension(self):
        validator = FileExtensionValidator()
        mock_file = MagicMock()
        mock_file.name = 'test.exe'
        with pytest.raises(DjangoValidationError):
            validator(mock_file)

    def test_case_insensitive(self):
        validator = FileExtensionValidator()
        mock_file = MagicMock()
        mock_file.name = 'test.JPG'
        validator(mock_file)

    def test_no_extension(self):
        validator = FileExtensionValidator()
        mock_file = MagicMock()
        mock_file.name = 'testfile'
        with pytest.raises(DjangoValidationError):
            validator(mock_file)
