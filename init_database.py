import sqlite3

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

user_table = '''create table user(
    id int primary key not null,
    name text not null, -- 注册必备
    password text not null, -- 注册必备
    phone_num text not null, -- 注册必备
    description char(100),
    user_type int not null, -- 1：普通用户 2：管理员 管理员只能后台注册
    identity_type int not null, -- 1：身份证 2：护照 注册必备
    identity_num text not null, -- 注册必备
    level int, -- 1-3等级逐渐增大
    city text not null, -- 注册必备
    signup_time text not null,
    modify_time text not null
);'''

callup_table = '''create table callup(
    id              integer         primary key     autoincrement,
    user_id         integer         not null,
    name            text            not null,
    type            integer         not null,
    description     text            not null,
    member          integer         not null,
    end_time        text            not null,
    img             text            not null,
    create_time     text            not null,
    modify_time     text            not null,
    state           integer         not null,       -- 1:已完成 2:待响应 3:已取消 4:到期未达成
    foreign key (user_id) references user(id) on update cascade on delete cascade
);'''

callup_request = '''create table callup_request(
    id              integer         primary key     autoincrement,
    callup_id       integer         not null,
    user_id         integer         not null,
    description     text            not null,
    create_time     text            not null,
    modify_time     text            not null,
    state           integer         not null,       -- 1:待处理 2:同意 3:拒绝 4:取消
    foreign key (callup_id) references callup(id) on update cascade on delete cascade, 
    foreign key (user_id) references user(id) on update cascade on delete cascade
);'''


user_HHX = '(1, "HHX", "hhx100", "12345678910", "", 2, 1, 111111111111111111, 3, "beijing", "2020-12-5", "2020-12-5")'
user_FB = '(2, "FB", "fb100", "12345678911", "", 2, 1, 111111111111111112, 3, "beijing", "2020-12-5", "2020-12-5")'

callup_1 = '(1, 3, "求web开发家教", 1, "找web前端工程师，辅导如何设计好看的前端，有偿！", 1, "2020-12-16", "webteacher.jpg", "2020-12-5", "2020-12-5", 2)'
callup_2 = '(2, 3, "求python开发家教", 1, "找python工程师，辅导，有偿！", 1, "2020-12-25", "pythonteacher.jpg", "2020-12-5", "2020-12-5", 2)'
callup_3 = '(3, 4, "求C++开发家教", 1, "找C++工程师，辅导，有偿！", 1, "2020-12-29", "cppteacher.jpg", "2020-12-5", "2020-12-5", 2)'

callup_req_1 = '(1, 2, 4, "我python贼好", "2020-12-14", "2020-12-14", 1)'
callup_req_2 = '(2, 2, 5, "我python更好", "2020-12-14", "2020-12-14", 1)'
callup_req_3 = '(3, 3, 3, "我会React", "2020-12-14", "2020-12-14", 1)'

if __name__ == '__main__':
    pass
    # create_table(callup_request)

    # insert_into_table("user", user_HHX)
    # insert_into_table("user", user_FB)
    # insert_into_table("callup", callup_1)
    # insert_into_table("callup", callup_2)
    # insert_into_table("callup", callup_3)
    # insert_into_table("callup_request", callup_req_1)
    # insert_into_table("callup_request", callup_req_2)
    # insert_into_table("callup_request", callup_req_3)

