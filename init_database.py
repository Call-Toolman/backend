import sqlite3
import random

DATABASE = 'database/callup_system.db'

def create_table(table_name):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute(table_name)
    db.commit()
    db.close()

def insert_into_table(table_name, values):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute('insert into ' + table_name + ' values ' + values)
    db.commit()
    db.close()




user_Admin = '(1, "admin", "admin", "12345678910", "I am admin", 2, 1, 500227111111111111,"lj", 2, "beijing","Community1", "2020-12-5", "2020-12-5")'
user_Normal = '(2, "user2", "user2", "12345678911", "I am normal", 1, 1, 511112111111111112,"zebgou", 1, "beijing","Community2", "2020-12-5", "2020-12-5")'

callup_1 = '(1, 3, "求web开发家教", 1, "找web前端工程师，辅导如何设计好看的前端，有偿！", 1, "2020-12-16", "webteacher.jpg", "2020-12-5", "2020-12-5", 2)'
callup_2 = '(2, 3, "求python开发家教", 1, "找python工程师，辅导，有偿！", 1, "2020-12-25", "pythonteacher.jpg", "2020-12-5", "2020-12-5", 2)'
callup_3 = '(3, 4, "求C++开发家教", 1, "找C++工程师，辅导，有偿！", 1, "2020-12-29", "cppteacher.jpg", "2020-12-5", "2020-12-5", 2)'

callup_req_1 = '(1, 2, 4, "我python贼好", "2020-12-14", "2020-12-14", 1)'
callup_req_2 = '(2, 2, 5, "我python更好", "2020-12-14", "2020-12-14", 1)'
callup_req_3 = '(3, 3, 3, "我会React", "2020-12-14", "2020-12-14", 1)'


city_list = ['北京市','上海市']
comm_list = [['海淀区','朝阳区','东城区','西城区'],['黄浦区', '徐汇区']]

month_map = [1,2,3,4,5,6,6,5,4,3,2,1]
type_map = [1.1,1.2,1.4,1.7,1.9]

def add_agency():
    idx = 1
    for city_index, city in enumerate(city_list):
        for comm in comm_list[city_index]:
            for type in range(1, 6):
                for year in range(2018, 2022):
                    for month in range(1,13):
                        new_city = city + "-" + city + "-" + comm
                        new_month = str(month) if month > 9 else "0" + str(month)
                        sql = f'({idx}, \"{year}-{new_month}\", \"{new_city}\", \"{comm}\", {type}, {type_map[type-1]*(random.randint(1,50) + 50 + month_map[month-1]*10)}, {type_map[type-1]*(random.randint(100,500) + 500 + month_map[month-1]*100)})'
                        idx += 1
                        insert_into_table("agency_earning", sql)



if __name__ == '__main__':
    # create_table(user_table)
    # create_table(callup_table)
    # create_table(callup_success)
    # create_table(callup_response)
    create_table(agency_earning)

    add_agency()
    # insert_into_table("user", user_Admin)
    # insert_into_table("user", user_Normal)
    # insert_into_table("callup", callup_1)
    # insert_into_table("callup", callup_2)
    # insert_into_table("callup", callup_3)
    # insert_into_table("callup_response", callup_req_1)
    # insert_into_table("callup_response", callup_req_2)
    # insert_into_table("callup_response", callup_req_3)
    pass
