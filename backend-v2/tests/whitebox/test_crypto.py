import pytest
import os
from unittest.mock import patch, MagicMock
from common.utils.crypto import decrypt_password


class TestDecryptPassword:
    def test_empty_string_returns_input(self):
        assert decrypt_password('') == ''

    def test_none_returns_input(self):
        assert decrypt_password(None) is None

    def test_no_colon_returns_input(self):
        assert decrypt_password('plainpassword') == 'plainpassword'

    def test_no_env_key_returns_input(self):
        with patch.dict(os.environ, {}, clear=True):
            if 'PASSWORD_ENCRYPT_KEY' in os.environ:
                del os.environ['PASSWORD_ENCRYPT_KEY']
            result = decrypt_password('abc123:encrypteddata')
            assert result == 'abc123:encrypteddata'

    @patch.dict(os.environ, {'PASSWORD_ENCRYPT_KEY': '0123456789abcdef0123456789abcdef'})
    def test_valid_encrypted_password(self):
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        import base64

        env_key = os.environ.get('PASSWORD_ENCRYPT_KEY', '')
        key = env_key.ljust(32, '0')[:32].encode('utf-8')
        iv = b'1234567890abcdef'
        plain_password = 'MySecret123'

        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(plain_password.encode('utf-8'), AES.block_size))
        encrypted_base64 = base64.b64encode(encrypted).decode('utf-8')

        time_hex = '1234567890abcdef'
        encrypted_data = f"{time_hex}:{encrypted_base64}"

        result = decrypt_password(encrypted_data)
        assert result == plain_password

    @patch.dict(os.environ, {'PASSWORD_ENCRYPT_KEY': 'short'})
    def test_short_key_padded_to_32(self):
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        import base64

        key = 'short'.ljust(32, '0')[:32].encode('utf-8')
        iv = b'1234567890abcdef'
        plain_password = 'TestPass1'

        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(plain_password.encode('utf-8'), AES.block_size))
        encrypted_base64 = base64.b64encode(encrypted).decode('utf-8')

        time_hex = '1234567890abcdef'
        encrypted_data = f"{time_hex}:{encrypted_base64}"

        result = decrypt_password(encrypted_data)
        assert result == plain_password

    @patch.dict(os.environ, {'PASSWORD_ENCRYPT_KEY': 'testkey123456789012345678901234'})
    def test_invalid_base64_returns_input(self):
        result = decrypt_password('1234567890abcdef:not_valid_base64!!!')
        assert result == '1234567890abcdef:not_valid_base64!!!'

    @patch.dict(os.environ, {'PASSWORD_ENCRYPT_KEY': 'testkey123456789012345678901234'})
    def test_corrupted_data_returns_input(self):
        result = decrypt_password('1234567890abcdef:YW55IGNhcm5hbCBwbGVhc3VyZQ==')
        assert isinstance(result, str)

    @patch.dict(os.environ, {'PASSWORD_ENCRYPT_KEY': 'testkey123456789012345678901234'})
    def test_time_hex_shorter_than_16(self):
        result = decrypt_password('abc:YW55IGNhcm5hbCBwbGVhc3VyZQ==')
        assert isinstance(result, str)
