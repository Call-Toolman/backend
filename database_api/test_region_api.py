def get_region(id):
    num = int(id[0:5])
    import sqlite3
    # 连接数据库(如果不存在则创建)
    conn = sqlite3.connect('../db_operation/region.db')
    cursor = conn.cursor()
    SQL= f'''select * from `region` where id={id}'''
    cursor.execute(SQL)
    re = cursor.fetchall()
    return re[0][1]

print(get_region('110107199908761234'))

