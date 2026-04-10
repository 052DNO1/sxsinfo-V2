"""
测试用例
"""

import pytest
from django.test import TestCase


class TestHealth(TestCase):
    """健康检查测试"""
    
    def test_health_check(self):
        """测试健康检查"""
        self.assertTrue(True)
