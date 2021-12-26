import sqlite3

# 连接数据库(如果不存在则创建)
conn = sqlite3.connect('region.db')
print("Opened database successfully")

# 创建游标
cursor = conn.cursor()
SQL= '''create table region(
     id int primary key not null,
     name text not null)
'''
cursor.execute(SQL)

# 关闭游标
cursor.close()
# 提交事物
conn.commit()
# 关闭连接
conn.close()
