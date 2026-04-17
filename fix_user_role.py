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
        print("Updating role for imported users...")
        print("Role: Teacher(1) + LabAdmin(2) = 3\n")
        
        cursor.execute("""
            UPDATE users 
            SET role = 3 
            WHERE username IN ('zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'qianqi', 
                               'sunba', 'zhoujiu', 'wushi', 'zheng11', 'feng12')
        """)
        
        affected_rows = cursor.rowcount
        connection.commit()
        
        print(f"Successfully updated {affected_rows} users\n")
        
        print("Verifying update:")
        print("=" * 60)
        cursor.execute("""
            SELECT username, nickname, role, department_id 
            FROM users 
            WHERE username IN ('zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'qianqi', 
                               'sunba', 'zhoujiu', 'wushi', 'zheng11', 'feng12')
            ORDER BY username
        """)
        users = cursor.fetchall()
        for user in users:
            role_display = []
            if user['role'] & 1: role_display.append('Teacher')
            if user['role'] & 2: role_display.append('LabAdmin')
            if user['role'] & 4: role_display.append('DeptAdmin')
            print(f"  {user['username']}: role={user['role']} ({'+'.join(role_display)}), dept_id={user['department_id']}")
        
        print("\nDone!")
            
except pymysql.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("\nDatabase connection closed.")
