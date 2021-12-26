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
    username text not null, -- 注册必备
    password text not null, -- 注册必备
    phone_num text not null, -- 注册必备
    description char(100),
    user_type int not null, -- 1：普通用户 2：管理员 管理员只能后台注册
    identity_type int not null, -- 1：身份证 2：护照 注册必备
    identity_num text not null, -- 注册必备
    real_name text not null, -- 注册必备
    level int, -- 1-2等级逐渐增大
    city text not null, -- 注册必备
    community text not null, --注册必备
    signup_time text not null,
    modify_time text not null
);'''

callup_table = '''create table callup(
    id              integer         primary key     autoincrement,
    callup_user_id         integer         not null,
    name            text            not null,
    type            integer         not null,
    description     text            not null,
    member          integer         not null,
    end_time        text            not null,
    img             text            not null,
    create_time     text            not null,
    modify_time     text            not null,
    state           integer         not null,       -- 1:已完成 2:待响应 3:已取消 4:到期未达成
    foreign key (callup_user_id) references user(id) on update cascade on delete cascade
);'''

callup_response = '''create table callup_response(
    id              integer         primary key     autoincrement,
    callup_id       integer         not null,
    response_user_id         integer         not null,
    description     text            not null,
    create_time     text            not null,
    modify_time     text            not null,
    state           integer         not null,       -- 1:待处理 2:同意 3:拒绝 4:取消
    foreign key (callup_id) references callup(id) on update cascade on delete cascade, 
    foreign key (response_user_id) references user(id) on update cascade on delete cascade
);'''


callup_success = '''create table callup_success(
    id              integer         primary key     autoincrement,
    callup_user_id       integer    not null,
    response_user_id     integer    not null,
    finish_time     text            not null,
    callup_fee      integer         not null,
    response_fee    integer         not null,
    foreign key (callup_user_id) references user(id) on update cascade on delete cascade
    foreign key (response_user_id) references user(id) on update cascade on delete cascade
);'''

agency_earning = '''create table agency_earning(
    id              integer         primary key     autoincrement,
    month           text            not null,
    city            text            not null,
    community       text            not null,
    type            integer         not null,
    finish_nums     int             not null,
    earning_fee     int             not null,
);'''

user_Admin = '(1, "admin", "admin", "12345678910", "I am admin", 2, 1, 500227111111111111,"lj", 2, "beijing","Community1", "2020-12-5", "2020-12-5")'
user_Normal = '(2, "user2", "user2", "12345678911", "I am normal", 1, 1, 511112111111111112,"zebgou", 1, "beijing","Community2", "2020-12-5", "2020-12-5")'

callup_1 = '(1, 3, "求web开发家教", 1, "找web前端工程师，辅导如何设计好看的前端，有偿！", 1, "2020-12-16", "webteacher.jpg", "2020-12-5", "2020-12-5", 2)'
callup_2 = '(2, 3, "求python开发家教", 1, "找python工程师，辅导，有偿！", 1, "2020-12-25", "pythonteacher.jpg", "2020-12-5", "2020-12-5", 2)'
callup_3 = '(3, 4, "求C++开发家教", 1, "找C++工程师，辅导，有偿！", 1, "2020-12-29", "cppteacher.jpg", "2020-12-5", "2020-12-5", 2)'

callup_req_1 = '(1, 2, 4, "我python贼好", "2020-12-14", "2020-12-14", 1)'
callup_req_2 = '(2, 2, 5, "我python更好", "2020-12-14", "2020-12-14", 1)'
callup_req_3 = '(3, 3, 3, "我会React", "2020-12-14", "2020-12-14", 1)'

if __name__ == '__main__':
    
    # create_table(user_table)
    # create_table(callup_table)
    # create_table(callup_success)
    # create_table(callup_response)
    create_table(agency_earning)
    # insert_into_table("user", user_Admin)
    # insert_into_table("user", user_Normal)
    # insert_into_table("callup", callup_1)
    # insert_into_table("callup", callup_2)
    # insert_into_table("callup", callup_3)
    # insert_into_table("callup_response", callup_req_1)
    # insert_into_table("callup_response", callup_req_2)
    # insert_into_table("callup_response", callup_req_3)

