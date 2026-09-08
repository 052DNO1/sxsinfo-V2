# Django settings 包
#
# 注意：不要在此文件无条件 import 任何环境配置（base/development/production/testing）。
# Python 加载 `lims.settings.<env>` 时会先执行本包 __init__.py；若在此 import development，
# 其顶层对共享 list 的就地修改（INSTALLED_APPS += / MIDDLEWARE.insert）会污染随后加载的
# production/testing 配置（实证：production 的 MIDDLEWARE 会混入 debug_toolbar）。
#
# 各环境文件自行 `from .base import *` 并覆盖所需项；通过 DJANGO_SETTINGS_MODULE 选择：
#   - manage.py        → lims.settings.development（默认，见 manage.py）
#   - wsgi.py / asgi.py → lims.settings.production
#   - pytest.ini       → lims.settings.testing
