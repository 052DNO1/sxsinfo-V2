import pymysql
from pymysql.cursors import DictCursor

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'wuhan',
    'password': '128076',
    'database': 'V2',
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**db_config, cursorclass=DictCursor)
    print("Database connected!\n")
    
    with connection.cursor() as cursor:
        print("=" * 80)
        print("Current user: wuhanhan info:")
        print("=" * 80)
        cursor.execute("""
            SELECT id, username, nickname, role, department_id, is_active
            FROM users 
            WHERE username = 'wuhanhan'
        """)
        wuhanhan = cursor.fetchone()
        if wuhanhan:
            print(f"ID: {wuhanhan['id']}")
            print(f"Username: {wuhanhan['username']}")
            print(f"Nickname: {wuhanhan['nickname']}")
            print(f"Role: {wuhanhan['role']} (4=Dept Admin)")
            print(f"Department ID: {wuhanhan['department_id']}")
            print(f"Is Active: {wuhanhan['is_active']}")
            
            dept_id = wuhanhan['department_id']
        else:
            print("User wuhanhan not found!")
            dept_id = None
        
        print("\n" + "=" * 80)
        print("Imported users info (zhangsan, lisi, wangwu, etc.):")
        print("=" * 80)
        cursor.execute("""
            SELECT id, username, nickname, role, department_id, is_active, created_at
            FROM users 
            WHERE username IN ('zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'qianqi', 
                               'sunba', 'zhoujiu', 'wushi', 'zheng11', 'feng12')
            ORDER BY created_at DESC
        """)
        imported_users = cursor.fetchall()
        
        for user in imported_users:
            print(f"\nUsername: {user['username']}")
            print(f"  Nickname: {user['nickname']}")
            print(f"  Role: {user['role']} (1=Teacher)")
            print(f"  Department ID: {user['department_id']}")
            print(f"  Is Active: {user['is_active']}")
            
            if dept_id is not None and user['department_id'] is None:
                print(f"  [PROBLEM] No department set! wuhanhan(dept_id={dept_id}) cannot see this user!")
            elif dept_id is not None and user['department_id'] != dept_id:
                print(f"  [PROBLEM] Different department! user dept={user['department_id']}, wuhanhan dept={dept_id}")
            else:
                print(f"  [OK] This user should be visible to wuhanhan")
        
        print("\n" + "=" * 80)
        print("Department info:")
        print("=" * 80)
        cursor.execute("SELECT id, name FROM departments")
        depts = cursor.fetchall()
        for dept in depts:
            print(f"Dept ID: {dept['id']}, Name: {dept['name']}")
            
except pymysql.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("\nDatabase connection closed.")
