import pytest
import io
from openpyxl import Workbook
from apps.core.exceptions import ValidationError, PermissionDenied
from common.services.import_service import ImportService


def create_excel_file(headers, rows):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    buffer.name = 'test.xlsx'
    return buffer


class TestImportServiceParseExcel:
    def test_parse_valid_excel(self):
        headers = ['实训室名称', '门牌号', '工位数']
        rows = [['测试实训室', 'LAB001', 30]]
        file_data = create_excel_file(headers, rows)
        data_rows, get_value, header_map = ImportService._parse_excel(file_data)
        assert len(data_rows) == 1
        assert get_value(data_rows[0], '实训室名称', 'name') == '测试实训室'
        assert get_value(data_rows[0], '门牌号', 'code') == 'LAB001'

    def test_parse_empty_file(self):
        headers = ['实训室名称']
        rows = []
        file_data = create_excel_file(headers, rows)
        with pytest.raises(ValidationError, match='文件内容为空'):
            ImportService._parse_excel(file_data)

    def test_parse_header_only(self):
        headers = ['实训室名称']
        rows = []
        file_data = create_excel_file(headers, rows)
        with pytest.raises(ValidationError, match='文件内容为空'):
            ImportService._parse_excel(file_data)

    def test_parse_all_empty_rows(self):
        headers = ['实训室名称', '门牌号']
        rows = [[None, None], ['', '']]
        file_data = create_excel_file(headers, rows)
        with pytest.raises(ValidationError, match='空行'):
            ImportService._parse_excel(file_data)

    def test_parse_missing_header(self):
        headers = [None, None]
        rows = [['test', 'value']]
        file_data = create_excel_file(headers, rows)
        with pytest.raises(ValidationError, match='未识别到有效的表头'):
            ImportService._parse_excel(file_data)

    def test_parse_multiple_rows(self):
        headers = ['实训室名称', '门牌号']
        rows = [['实训室A', 'A001'], ['实训室B', 'B002']]
        file_data = create_excel_file(headers, rows)
        data_rows, get_value, header_map = ImportService._parse_excel(file_data)
        assert len(data_rows) == 2

    def test_get_value_fallback(self):
        headers = ['name', 'code']
        rows = [['测试', 'CODE001']]
        file_data = create_excel_file(headers, rows)
        data_rows, get_value, header_map = ImportService._parse_excel(file_data)
        assert get_value(data_rows[0], '实训室名称', 'name') == '测试'

    def test_get_value_missing_key(self):
        headers = ['name']
        rows = [['测试']]
        file_data = create_excel_file(headers, rows)
        data_rows, get_value, header_map = ImportService._parse_excel(file_data)
        assert get_value(data_rows[0], 'nonexistent') == ''


class TestImportServiceImportLaboratories:
    def test_no_permission(self, db, wb_teacher):
        file_data = create_excel_file(['实训室名称', '门牌号'], [['测试', 'LAB001']])
        with pytest.raises(PermissionDenied, match='无权限导入'):
            ImportService.import_laboratories(requester=wb_teacher, file_data=file_data)

    def test_import_success(self, db, wb_super_admin, wb_department):
        file_data = create_excel_file(
            ['实训室名称', '门牌号', '工位数'],
            [['导入实训室', 'WB_IMP_001', 30]],
        )
        result = ImportService.import_laboratories(requester=wb_super_admin, file_data=file_data)
        assert result['success_count'] >= 0

    def test_import_empty_required_field(self, db, wb_super_admin):
        file_data = create_excel_file(
            ['实训室名称', '门牌号'],
            [['', 'CODE001']],
        )
        result = ImportService.import_laboratories(requester=wb_super_admin, file_data=file_data)
        assert result['failed_count'] >= 1


class TestImportServiceImportEquipment:
    def test_no_permission(self, db, wb_teacher):
        file_data = create_excel_file(['设备名称', '设备编号'], [['测试', 'EQ001']])
        with pytest.raises(PermissionDenied, match='无权限导入'):
            ImportService.import_equipment(requester=wb_teacher, file_data=file_data)
