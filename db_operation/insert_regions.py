import sqlite3

# 连接数据库(如果不存在则创建)
conn = sqlite3.connect('region.db')
print("Opened database successfully")

# 创建游标
cursor = conn.cursor()
# SQL= '''select * from `region` where id=110107
# '''
SQL = open('../sql_scripts/insert.sql','r',encoding='utf-8').read()
cursor.execute(SQL)
re = cursor.fetchall()
print(re)

# 关闭游标
cursor.close()
# 提交事物
conn.commit()
# 关闭连接
conn.close()
