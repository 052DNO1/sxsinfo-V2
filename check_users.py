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
    print("数据库连接成功！\n")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        user_count = result['count']
        print(f"用户总数: {user_count}\n")
        
        if user_count > 0:
            cursor.execute("""
                SELECT id, username, nickname, email, phone, role, status, 
                       is_active, is_superuser, created_at, last_login
                FROM users
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
            
            print("=" * 100)
            print("用户列表:")
            print("=" * 100)
            
            for user in users:
                print(f"\nID: {user['id']}")
                print(f"用户名: {user['username']}")
                print(f"昵称: {user['nickname'] or '(未设置)'}")
                print(f"邮箱: {user['email'] or '(未设置)'}")
                print(f"手机: {user['phone'] or '(未设置)'}")
                print(f"角色: {user['role']}")
                print(f"状态: {user['status']}")
                print(f"是否激活: {'是' if user['is_active'] else '否'}")
                print(f"是否超级管理员: {'是' if user['is_superuser'] else '否'}")
                print(f"创建时间: {user['created_at']}")
                print(f"最后登录: {user['last_login'] or '(从未登录)'}")
                print("-" * 100)
        else:
            print("数据库中没有用户！")
            
except pymysql.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("\n数据库连接已关闭。")
