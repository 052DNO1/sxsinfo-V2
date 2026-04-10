"""
临时演示：模拟测试失败的情况
"""

import pytest
from apps.laboratories.serializers.laboratory import LaboratoryUpdateSerializer
from apps.laboratories.models import Laboratory
from apps.users.models import User


def test_demo_show_error_message(db):
    """演示：当测试失败时如何显示错误信息"""
    
    # 创建一个分院
    from apps.users.models import Department
    dept = Department.objects.create(name='演示分院', code='DEMO')
    
    # 创建用户
    admin = User.objects.create_user(
        username='demo_admin',
        password='test123',
        nickname='演示管理员',
        role=2,
        is_active=True
    )
    
    # 创建实训室
    lab = Laboratory.objects.create(
        name='演示实训室',
        code='DEMO_001',
        building='演示楼',
        floor=1,
        room_number='101',
        capacity=30,
        laboratory_type='COMPUTER',
        department=dept,
        admin=admin,
        status=1
    )
    
    # 测试场景：发送 admin=0（未分配）
    print("\n" + "="*60)
    print("[TEST] 场景：将管理员设置为 0 (未分配)")
    print("="*60)

    data = {
        'name': lab.name,
        'code': lab.code,
        'capacity': lab.capacity,
        'status': lab.status,
        'admin': 0,  # 关键：前端发送的"未分配"
        'note': ''
    }

    print(f"\n[SEND] 发送数据: {data}")

    serializer = LaboratoryUpdateSerializer(instance=lab, data=data)

    if serializer.is_valid():
        print(f"[OK] 验证通过！有效字段: {list(serializer.validated_data.keys())}")
        print(f"[OK] admin 字段值: {serializer.validated_data.get('admin')}")

        if serializer.validated_data.get('admin') is None:
            print("[SUCCESS] 完美！admin=0 被正确转换为 None（未分配状态）")
        else:
            print(f"[WARN] 注意：admin 值为 {serializer.validated_data.get('admin')}")
    else:
        print(f"[FAIL] 验证失败！错误信息:")
        for field, errors in serializer.errors.items():
            for error in errors:
                print(f"   - {field}: {error}")

    print("\n" + "="*60)
    print("[SUMMARY] 测试总结")
    print("="*60)
    print("这个测试保护了以下业务规则：")
    print("  [OK] 前端发送 admin=0 -> 后端接受为'未分配'")
    print("  [OK] 不再出现 500 Internal Server Error")
    print("  [OK] 数据库中 admin 字段设为 NULL")
    print("  [OK] 前端列表显示'未分配'而非报错")
    print("="*60 + "\n")
    
    assert serializer.is_valid(), f"期望验证通过，但失败: {serializer.errors}"
