# 🧪 后端测试架构完整指南

## 📖 目录
1. [为什么需要测试？](#为什么需要测试)
2. [测试架构总览](#测试架构总览)
3. [快速开始](#快速开始)
4. [测试分层详解](#测试分层详解)
5. [如何运行测试](#如何运行测试)
6. [如何编写新测试](#如何编写新测试)
7. [常见问题 FAQ](#常见问题-faq)

---

## 为什么需要测试？

### 😱 **没有测试的痛苦**
- ❌ 改了一行代码，不知道哪里会出问题
- ❌ 修复一个 bug，引入两个新 bug
- ❌ 重构代码时提心吊胆，生怕搞崩系统
- ❌ 每次修改都要手动测试所有功能

### ✅ **有了测试的好处**
- ✅ **放心改代码**：改完跑一遍测试就知道有没有破坏功能
- ✅ **快速定位 bug**：测试会告诉你哪一行出了问题
- ✅ **文档化业务规则**：测试用例就是最好的需求文档
- ✅ **重构信心**：有测试保障，大胆优化代码结构
- ✅ **团队协作**：新人看测试就能理解业务逻辑

### 💡 **真实案例：刚才的 500 错误**
刚才我们就是通过**单元测试**快速定位到：
1. `admin=0` 导致 Serializer 验证失败
2. 根本原因：`PrimaryKeyRelatedField` 不接受 0 值
3. 解决方案：自定义验证器处理"未分配"状态
4. **验证修复**：跑测试确认不再报错 → 全部通过！✅

---

## 测试架构总览

```
backend-v2/
└── tests/                          # 测试根目录
    ├── conftest.py                 # 🔑 全局配置和 fixtures
    │
    ├── unit/                       # 📦 单元测试（最快）
    │   ├── test_serializers/       #    序列化器测试
    │   │   └── test_laboratory_serializer.py
    │   ├── test_services/          #    服务层测试
    │   │   ├── test_laboratory_service.py
    │   │   └── test_user_service.py
    │   └── test_models/            #    模型测试
    │
    ├── integration/                # 🔗 集成测试（中等速度）
    │   └── test_laboratory_crud.py #    完整 CRUD 流程
    │
    └── e2e/                        # 🌐 端到端测试（最慢但最真实）
        └── test_laboratory_api.py  #    模拟 HTTP 请求
```

### 三层测试金字塔

```
        /\
       /  \         E2E 测试 (少而精)
      /────\         模拟真实用户操作
     /  🌐  \
    /────────\       
   / 集成测试 \      (适中)
  /   🔗     \     测试模块间协作
 /────────────\
/   单元测试    \   (多而快)
/  📦 📦 📦 📦  \  测试单个函数/方法
/______________\
```

---

## 快速开始

### 第一步：安装测试依赖

```bash
cd backend-v2
pip install -r tests/requirements-test.txt
```

### 第二步：配置测试数据库（可选）

在 `lims/settings/test.py` 中配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # 使用内存数据库，超快！
    }
}
```

### 第三步：运行所有测试

```bash
cd backend-v2
pytest tests/ -v
```

### 第四步：查看测试报告

```bash
pytest tests/ -v --cov=apps --cov-report=html
# 会生成 htmlcov/index.html，浏览器打开即可看到覆盖率报告
```

---

## 如何运行测试

### 1️⃣ 运行全部测试

```bash
pytest tests/ -v
```

### 2️⃣ 只运行某个模块的测试

```bash
# 只运行实训室相关测试
pytest tests/unit/test_serializers/test_laboratory_serializer.py -v

# 只运行服务层测试
pytest tests/unit/test_services/ -v
```

### 3️⃣ 只运行包含特定关键词的测试

```bash
# 只运行与"admin"相关的测试
pytest tests/ -v -k "admin"

# 只运行与"未分配"相关的测试
pytest tests/ -v -k "unassigned or none"
```

### 4️⃣ 运行并显示详细输出

```bash
pytest tests/ -v -s  # -s 显示 print 输出
```

### 5️⃣ 运行直到第一个失败就停止

```bash
pytest tests/ -x  # 遇到第一个错误立即停止
```

### 6️⃣ 生成覆盖率报告

```bash
pytest tests/ --cov=apps --cov-report=term-missing
# 会显示哪些代码没有被测试覆盖到
```

---

## 测试分层详解

### 📦 **第一层：单元测试 (Unit Tests)**

**特点**：
- ⚡ 最快（毫秒级）
- 🔬 测试最小单元（函数、方法）
- 🎯 精确定位问题
- 🚫 不依赖外部资源（数据库、网络）

**适合测试**：
- ✅ 字段验证逻辑
- ✅ 数据转换逻辑
- ✅ 业务规则判断
- ❌ 数据库交互（交给集成测试）

**示例**：[test_laboratory_serializer.py](test_laboratory_serializer.py)

```python
def test_admin_none_should_pass(self, lab_instance):
    """测试 admin=None (未分配) - 应该通过"""
    data = {'name': '...', 'admin': None, ...}
    
    serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
    
    assert serializer.is_valid()  # 如果这里失败，说明验证器有bug
    assert serializer.validated_data['admin'] is None
```

**什么时候写？**
- 每次修复 bug 后，写测试防止回归
- 每次新增字段验证规则后，写边界测试
- 每次遇到复杂业务逻辑时，写测试记录预期行为

---

### 🔗 **第二层：集成测试 (Integration Tests)**

**特点**：
- ⏱️ 中等速度（秒级）
- 🔗 测试多个组件协作
- 📊 使用真实数据库
- 🎯 验证端到端流程

**适合测试**：
- ✅ 完整的 CRUD 工作流
- ✅ Service 层 + Model 层协作
- ✅ 数据一致性
- ✅ 复杂业务场景

**示例**：[test_laboratory_crud.py](test_laboratory_crud.py)

```python
def test_complete_create_read_update_delete_workflow(...):
    """测试完整生命周期：创建→读取→更新→删除"""
    
    # Step 1: 创建
    lab = service.create_laboratory(...)
    
    # Step 2: 读取
    detail = service.get_laboratory_detail(lab_id)
    
    # Step 3: 更新（包括取消管理员）
    updated = service.update_laboratory(lab_id, admin=None)
    
    # Step 4: 删除
    service.delete_laboratory(lab_id)
```

**什么时候写？**
- 新增重要功能后
- 跨多个模块的业务流程
- 需要验证数据一致性时

---

### 🌐 **第三层：端到端测试 (E2E Tests)**

**特点**：
- 🐢 最慢（可能需要几秒到几十秒）
- 🌐 完全模拟 HTTP 请求
- 🔐 包含认证和权限验证
- 🎯 最接近真实用户体验

**适合测试**：
- ✅ API 接口完整性
- ✅ 认证授权流程
- ✅ 错误响应格式
- ✅ 权限控制

**示例**：[test_laboratory_api.py](test_laboratory_api.py)

```python
def test_update_laboratory_set_admin_to_none(
    self, authenticated_client, test_laboratory
):
    """
    通过 API 将管理员设置为 None
    
    完全模拟前端操作！
    """
    update_data = {
        'name': test_laboratory.name,
        'admin': None,  # 前端选择"未分配"
        ...
    }
    
    response = authenticated_client.put(
        f'/api/laboratories/{test_laboratory.id}/',
        update_data,
        format='json'
    )
    
    # 关键断言：不再是 500 错误！
    assert response.status_code == 200
```

**什么时候写？**
- API 接口开发完成后
- 需要验证前后端对接是否正确
- 测试安全性和权限控制时

---

## 如何编写新测试

### 场景 1：你刚修复了一个 Bug

**步骤**：

1️⃣ **先写测试复现 Bug**

```python
# tests/unit/test_serializers/test_xxx_serializer.py

def test_bug_fix_admin_zero_causes_500(self, lab_instance):
    """
    Bug: 发送 admin=0 时返回 500 错误
    期望：应该正常处理，返回 200
    """
    data = {
        'name': lab_instance.name,
        'admin': 0,  # 这个值之前会导致 500 错误
        ...
    }
    
    serializer = XxxSerializer(instance=lab_instance, data=data)
    
    # 这个断言会在修复前失败，修复后通过 ✅
    assert serializer.is_valid(), f"Bug 未修复: {serializer.errors}"
```

2️⃣ **运行测试确认失败**

```bash
pytest tests/ -v -k "bug_fix_admin_zero"
# 应该看到 FAILED
```

3️⃣ **修复代码**

4️⃣ **再次运行测试确认通过**

```bash
pytest tests/ -v -k "bug_fix_admin_zero"
# 现在应该看到 PASSED ✅
```

5️⃣ **提交代码，测试永久保护这段逻辑**

---

### 场景 2：你要新增一个功能

**步骤**：

1️⃣ **先写测试定义预期行为**

```python
def test_new_feature_should_work(self):
    """新功能：当 XXX 时，应该 YYY"""
    # 准备数据
    # 执行操作
    # 断言结果
```

2️⃣ **实现功能**

3️⃣ **运行测试直到通过**

4️⃣ **补充边界情况测试**

```python
def test_new_feature_edge_case_1(self):
    """边界情况 1：空值"""

def test_new_feature_edge_case_2(self):
    """边界情况 2：无效输入"""

def test_new_feature_edge_case_3(self):
    """边界情况 3：并发场景"""
```

---

### 场景 3：你要重构代码

**步骤**：

1️⃣ **先确保现有测试都通过**

```bash
pytest tests/ -v
# 所有测试必须都是 PASSED
```

2️⃣ **重构代码**

3️⃣ **再次运行测试**

```bash
pytest tests/ -v
# 如果还是全部 PASSED，说明重构成功！✅
# 如果有 FAILED，说明重构破坏了某些行为
```

---

## 测试最佳实践 ✨

### ✅ DO（推荐做法）

1. **测试命名要清晰**
   ```python
   def test_admin_none_should_pass(self):  # ✅ 清晰
   def test_1(self):  # ❌ 不知道测什么
   ```

2. **一个测试只测一件事**
   ```python
   def test_admin_validation(self):  # ✅ 单一职责
   def test_admin_and_name_and_code_and_status(self):  # ❌ 太复杂
   ```

3. **使用有意义的断言信息**
   ```python
   assert response.status_code == 200, f"期望200，实际{response.status_code}"  # ✅
   assert response.status_code == 200  # ❌ 失败时不知道原因
   ```

4. **使用 fixtures 复用数据**
   ```python
   @pytest.fixture
   def test_laboratory(db):  # ✅ 复用
       return Laboratory.objects.create(...)
   
   def test_xxx(self, test_laboratory):  # 自动注入
       pass
   ```

5. **测试边界情况**
   ```python
   def test_admin_none(self): ...      # None
   def test_admin_zero(self): ...      # 0
   def test_admin_empty_string(self): ...  # ''
   def test_admin_invalid_id(self): ...   # 无效ID
   ```

### ❌ DON'T（避免的做法）

1. **不要测试实现细节**
   ```python
   def test_internal_method_called(self):  # ❌ 测试内部实现
       assert mock_function.called
   
   def test_result_is_correct(self):  # ✅ 测试最终结果
       assert result['status'] == 'success'
   ```

2. **不要依赖测试执行顺序**
   ```python
   # ❌ 依赖顺序
   def test_step1_create(self): ...
   def test_step2_update(self): ...  # 假设 step1 已执行
   
   # ✅ 每个测试独立
   def test_create(self): ...  # 自己创建数据
   def test_update(self): ...  # 自己创建数据
   ```

3. **不要忽略失败的测试**
   ```bash
   # ❌ 看到失败不管
   pytest tests/  # 有 FAILED 但继续改代码
   
   # ✅ 立即修复或标记为 xfail
   pytest.mark.xfail(reason="已知问题，待修复")
   ```

---

## 常见问题 FAQ

### Q1: 测试太慢了怎么办？

**A**: 
- 多写**单元测试**（最快），少写 E2E 测试
- 使用 SQLite 内存数据库（已在 conftest.py 配置）
- 并行运行测试：`pytest tests/ -n auto`（需安装 pytest-xdist）

### Q2: 测试总是失败怎么办？

**A**:
1. 先看错误信息：`pytest tests/ -v` 会显示详细错误
2. 检查 fixtures 是否正确加载数据
3. 查看是否有数据库残留：`pytest tests/ --create-db`
4. 单独运行失败的测试：`pytest tests/xxx.py::TestClass::test_method -v -s`

### Q3: 需要每次改代码都跑测试吗？

**A**:
- **提交前**：必须跑一次全量测试
- **开发中**：可以只跑相关模块的测试
- **CI/CD**：自动跑全量测试（推荐配置 GitHub Actions）

### Q4: 测试覆盖率要达到多少？

**A**:
- 核心业务逻辑：**80%+**
- 一般代码：**60%+**
- 工具函数：**90%+**
- 不要盲目追求 100%，关键是**覆盖重要路径**

### Q5: 如何测试需要登录的接口？

**A**: 已经在 `conftest.py` 中配置好了！

```python
def test_authenticated_endpoint(self, authenticated_client):
    """authenticated_client 自动携带认证信息"""
    response = authenticated_client.get('/api/some-protected-endpoint/')
    assert response.status_code == 200
```

### Q6: 可以在生产环境数据库上跑测试吗？

**A**: **绝对不行！** 🚫
- 测试会创建/删除数据
- 可能破坏生产数据
- 始终使用测试数据库或 SQLite 内存数据库

---

## 🎯 下一步行动

### 立即可以做的事：

1. **运行现有测试**，看看有多少通过
   ```bash
   cd backend-v2
   pytest tests/ -v
   ```

2. **为最近修复的功能添加测试**
   - 比如"未分配管理员"功能的测试已经写好了 ✅

3. **为即将开发的功能先写测试**（TDD - 测试驱动开发）

4. **配置 CI/CD 自动化测试**（可选但推荐）

---

## 📚 学习资源

- [Pytest 官方文档](https://docs.pytest.org/)
- [Django 测试工具](https://docs.djangoproject.com/en/stable/topics/testing/)
- [测试驱动开发实战](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)

---

## 🤝 贡献指南

添加新测试时请遵循：

1. 在正确的目录下创建文件
2. 遵循命名规范：`test_<模块名>.py`
3. 每个测试函数要有清晰的 docstring
4. 使用已有的 fixtures
5. 提交前确保所有测试通过

---

**祝测试愉快！🎉 有了这套测试体系，你可以放心大胆地改代码了！**
