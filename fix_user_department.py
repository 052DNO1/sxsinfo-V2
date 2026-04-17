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
        print("Updating department_id for imported users...\n")
        
        cursor.execute("""
            UPDATE users 
            SET department_id = 1 
            WHERE username IN ('zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'qianqi', 
                               'sunba', 'zhoujiu', 'wushi', 'zheng11', 'feng12')
        """)
        
        affected_rows = cursor.rowcount
        connection.commit()
        
        print(f"Successfully updated {affected_rows} users to department_id = 1\n")
        
        print("Verifying update:")
        print("=" * 60)
        cursor.execute("""
            SELECT username, nickname, department_id 
            FROM users 
            WHERE username IN ('zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'qianqi', 
                               'sunba', 'zhoujiu', 'wushi', 'zheng11', 'feng12')
            ORDER BY username
        """)
        users = cursor.fetchall()
        for user in users:
            print(f"  {user['username']}: department_id = {user['department_id']}")
        
        print("\nDone! These users should now be visible to wuhanhan.")
            
except pymysql.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("\nDatabase connection closed.")
