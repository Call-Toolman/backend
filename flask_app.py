from typing_extensions import Required
from flask import Flask, g, request
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs
from utils import *
import flask_cors
import flask_restful as restful
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity, get_jwt,
                                decode_token)
import sqlite3
import numpy as np

DATABASE = 'database/callup_system.db'

app = Flask(__name__)
api = restful.Api(app)

flask_cors.CORS(app, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)


@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/ttt', methods=["POST"])
def ttt():
    print(request.args, '--args')

    return {'status': 'ok'}
    


def query_db(query, args=(), onlyonerow=False):
    c = g.db.execute(query, args)
    rv = [
        dict((c.description[idx][0], value) for idx, value in enumerate(row))
        for row in c.fetchall()
    ]
    return (rv[0] if rv else None) if onlyonerow else rv


def get_username_from_token():
    token = request.headers.get("Authorization").split(' ')[-1]
    return decode_token(token)['sub']


class HandleUserSignup(restful.Resource):
    @use_args(
        {
            'username': fields.Str(required=True),
            'password': fields.Str(required=True),
            'phone_num': fields.Str(required=True),
            'description': fields.Str(required=True),
            'real_name': fields.Str(required=True),
            'identity_type': fields.Integer(required=True),
            'identity_num': fields.Str(required=True),
            'city': fields.List(fields.Str())
            # 'community': fields.Str(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        args["city"] = list2city(args["city"])
        userexist = query_db(
            'select count(*) as count from user where username = ?',
            (args['username'], ),
            onlyonerow=True)['count']
        if userexist == 1:
            return {'status': 'error', 'error_message': '用户名已存在'}
        else:
            userNum = query_db('select count(*) as count from user',
                               onlyonerow=True)['count']
            newID = userNum + 1
            userType = 1
            nowTime = query_db('select date("now") as now',
                               onlyonerow=True)['now']
            c = g.db.cursor()
            c.execute(
                'insert into user (id, username, password, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, signup_time, modify_time, community) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, " ")',
                (newID, args['username'], args['password'], args['phone_num'],
                 args['description'], args['real_name'], userType,
                 args['identity_type'], args['identity_num'], 1, args['city'],
                 nowTime, nowTime))
            g.db.commit()
            return {'status': 'ok'}


class CheckUserSignin(restful.Resource):
    @use_args(
        {
            'username': fields.Str(required=True),
            'password': fields.Str(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        userexist = query_db(
            'select count(*) as count from user where username = ?',
            (args['username'], ),
            onlyonerow=True)['count']
        if userexist == 1:
            rightpassword = query_db(
                'select count(*) as count from user where username = ? and password = ?',
                (args['username'], args['password']),
                onlyonerow=True)['count']
            if rightpassword == 1:
                access_token = create_access_token(identity=args["username"])
                refresh_token = create_refresh_token(identity=args["username"])

                userinfo = query_db(
                    'select id, username, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user where username = ?',
                    (args['username'], ))[0]
                usertype = 'user' if userinfo["user_type"] == 1 else 'admin'
                return {
                    'status': 'ok',
                    'current_authority': usertype,
                    'access_token': access_token
                }
            else:
                return {'status': 'error', 'error_message': '密码错误'}
        else:
            return {'status': 'error', 'error_message': '用户名不存在'}


class GetProfile(restful.Resource):
    @jwt_required()
    def get(self):
        # userinfo
        username = get_username_from_token()

        print("username ", username)
        userinfo = query_db(
            'select id, username, signup_time, modify_time, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user where username = ?',
            (username, ))[0]
        usertype = 'user' if userinfo["user_type"] == 1 else 'admin'
        userinfo["city"] = city2list(userinfo["city"])
        userinfo["user_type"] = usertype
        return userinfo


class UpdateUserInfo(restful.Resource):
    @jwt_required()
    @use_args(
        {
            'username': fields.Str(required=True),
            'password': fields.Str(required=True, allow_none=True),
            'phone_num': fields.Str(required=True),
            'description': fields.Str(required=True, allow_none=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        if args['password']:
            c = g.db.cursor()
            c.execute(
                'update user set password = ?, phone_num = ? , description = ? , modify_time = ? where username = ?',
                (args['password'], args['phone_num'], args['description'],
                 nowTime, args['username']))
            g.db.commit()
        else:
            c = g.db.cursor()
            c.execute(
                'update user set phone_num = ? , description = ? , modify_time = ? where username = ?',
                (args['phone_num'], args['description'], nowTime,
                 args['username']))
            g.db.commit()

        userinfo = query_db(
            'select id, username, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user where username = ?',
            (args['username'], ))
        userinfo[0]["city"] = city2list(userinfo[0]["city"])
        return userinfo[0]


class GetUserList(restful.Resource):
    @jwt_required()
    def get(self):
        userinfo = query_db(
            'select id, username, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user'
        )
        return {'status': 'ok', 'userinfo': userinfo}


class AddRequest(restful.Resource):
    @jwt_required()
    @use_args(
        {
            'title': fields.Str(required=True),
            'type': fields.Str(required=True),
            'endtime': fields.Str(required=True),
            'description': fields.Str(required=True),
            'population': fields.Str(required=True),
            'img': fields.Str(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        args["username"] = get_username_from_token()
        print(args)
        userID = str(
            query_db('select id from user where username = ?',
                     (args['username'], ),
                     onlyonerow=True)['id'])
        name = args['title']
        type = str(args['type'])
        description = args['description']
        member = str(args['population'])
        endTime = args['endtime']
        img = args['img']
        createTime = query_db('select date("now") as now',
                              onlyonerow=True)['now']
        modifyTime = createTime
        state = str(2)

        print(userID, name, type, description, member, endTime, img,
              createTime, modifyTime, state)
        c = g.db.cursor()
        c.execute(
            '''insert into callup (callup_user_id,name,type,description,member,end_time,img,create_time,
        modify_time,state) values (?,?,?,?,?,?,?,?,?,?)''',
            (userID, name, type, description, member, endTime, img, createTime,
             modifyTime, state))
        g.db.commit()
        return {'status': 'ok'}


class CancelRequst(restful.Resource):
    @jwt_required()
    @use_args(
        {
            'id':fields.Integer(required=True)
        }
    )
    def post(self, args):
        print(args['id'])
        c = g.db.cursor()
        c.execute("update callup set state = 3 where id = ?",
                  (args['id'],))
        g.db.commit()
        return {'status': 'ok'}


    
class UpdateCallUp(restful.Resource):
    @jwt_required()
    @use_args(
        {
            'id': fields.Str(required=True),
            'title': fields.Str(required=True),
            'type': fields.Str(required=True),
            'endtime': fields.Str(required=True),
            'description': fields.Str(required=True),
            'population': fields.Str(required=True),
            'img': fields.Str(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        id = args['id']
        name = args['title']
        type = str(args['type'])
        description = args['description']
        member = str(args['population'])
        endTime = args['endtime']
        img = args['img']
        modifyTime = query_db('select date("now") as now',
                              onlyonerow=True)['now']

        print(id, name, type, description, member, endTime, img, modifyTime)
        c = g.db.cursor()
        c.execute(
            '''
            update callup 
            set name=?,type=?,description=?,member=?,end_time=?,img=?,modify_time=?
            where id=?''',
            (name, type, description, member, endTime, img, modifyTime, id))
        g.db.commit()
        return {'status': 'ok'}


class GetCallupList(restful.Resource):
    @jwt_required()
    def get(self):
        callupinfo = query_db(
            'select callup.id as id, user.username as owner, user.id as owner_id, callup.name as name, callup.type as type, user.city as city, callup.description as description, callup.member as member, end_time, img, create_time as ctime, callup.modify_time as mtime, callup.state as state from user inner join callup on user.id = callup.callup_user_id'
        )
        for i in range(len(callupinfo)):
            callupinfo[i]['requests'] = query_db(
                'select c.id as id, c.response_user_id as user_id, u.username as user_name, c.description as description, c.state as state from callup_response as c inner join user as u on c.response_user_id = u.id where callup_id = ?',
                (callupinfo[i]['id'], ))

        return {'status': 'ok', 'callupinfo': callupinfo}


# TODO 多个用户同时申请保留一个
class AddResponse(restful.Resource):
    @jwt_required()
    @use_args(
        {
            'id': fields.Integer(required=True),
            'user': fields.Str(required=True),
            'description': fields.Str(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        print(args['description'])
        userID = query_db('select id from user where username = ?',
                          (args['user'], ),
                          onlyonerow=True)['id']
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        c = g.db.cursor()
        c.execute(
            "insert into callup_response (callup_id, response_user_id, description, create_time, modify_time, state) values (?, ?, ?, ?, ?, ?)",
            (args['id'], userID, args['description'], nowTime, nowTime, 1))
        g.db.commit()
        return {'status': 'ok'}


class UpdateResponse(restful.Resource):
    @jwt_required()
    @use_args(
        {
            'id': fields.Integer(required=True),
            'description': fields.Str(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        c = g.db.cursor()
        c.execute(
            "update callup_response set description = ? , modify_time = ? where id = ?",
            (args['description'], nowTime, args['id']))
        g.db.commit()
        return {'status': 'ok'}


class ManageResponse(restful.Resource):
    # @jwt_required()
    @use_args(
        {
            'id': fields.Integer(required=True),
            'state': fields.Integer(required=True)
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        c = g.db.cursor()
        c.execute("update callup_response set state = ? where id = ?",
                  (args['state'], args['id']))
        g.db.commit()
        if args['state'] == 2:
            c = g.db.cursor()
            callup_response = query_db(
                'select * from callup_response where id = ?', (args['id'], ),
                onlyonerow=True)
            callup_id = callup_response["callup_id"]
            callup = query_db('select * from callup where id = ?',
                              (callup_id, ),
                              onlyonerow=True)
            nowTime = query_db('select date("now") as now',
                               onlyonerow=True)['now']
            nowMonth = nowTime.split('-')[0] + "-" + nowTime.split('-')[1]
            user = query_db('select * from user where id = ?',
                            (callup['callup_user_id'], ),
                            onlyonerow=True)
            c.execute("update callup set state = 1 where id = ?",
                      (callup_id, ))
            c.execute(
                "insert into callup_success (callup_user_id, response_user_id, finish_time, callup_fee, response_fee) values (?, ?, ?, ?, ?)",
                (callup['callup_user_id'], callup_response["response_user_id"],
                 nowTime, callup["member"] * 3, 1))
            exits = query_db(
                'select count(*) as count from agency_earning where city = ? and type = ? and month = ?',
                (user['city'], callup["type"], nowMonth),
                onlyonerow=True)['count']
            if exits == 0:
                c.execute(
                    "insert into agency_earning (month, city, type, community, finish_nums, earning_fee) values (?, ?, ?,?, ?, ?)",
                    (nowMonth, user['city'], callup["type"],
                     city2list(user['city'][-1]), 0, 0))
            c.execute(
                "update agency_earning set finish_nums = finish_nums+1, earning_fee = earning_fee + ? where city = ? and type = ? and month = ?",
                (str(callup["member"] * 3 + 1), user['city'], callup["type"],
                 nowMonth))
            g.db.commit()
        return {'status': 'ok'}


class CallUpStastic(restful.Resource):
    @jwt_required()
    @use_args({'month': fields.Str(required=True)},
              location='json',
              unknown="EXCLUDE")
    def get(self, args):
        profit = {}
        if args['month'] == "all":
            c = g.db.cursor()
            for i in range(1, 6):
                c.execute(
                    "select sum(4*member) as sum from callup where state = 1 and type = ?",
                    (str(i)))
                temp = [
                    dict((c.description[idx][0], value)
                         for idx, value in enumerate(row))
                    for row in c.fetchall()
                ][0]['sum']
                profit[i] = temp if temp else 0
            g.db.commit()
        else:
            c = g.db.cursor()
            for i in range(1, 6):
                c.execute(
                    "select sum(4*member)  as sum from callup where state = 1 and type = ? and end_time like ?",
                    (str(i), args['month']))
                temp = [
                    dict((c.description[idx][0], value)
                         for idx, value in enumerate(row))
                    for row in c.fetchall()
                ][0]['sum']
                profit[i] = temp if temp else 0
            g.db.commit()
        return {'result': 'ok', 'profit': profit}


class Statistic(restful.Resource):
    # @jwt_required()
    @use_args(
        {
            'start_time': fields.Str(required=True),
            'end_time': fields.Str(required=True),
            'city': fields.List(fields.Str())
        },
        location='json',
        unknown="EXCLUDE")
    def post(self, args):
        feePerType = []
        feePerMonth = []
        city = list2city(args["city"])
        pattern = city + '%'
        for type in range(1, 6):
            agency_earning = query_db(
                "select sum(finish_nums) as num_sum, sum(earning_fee) as fee_sum from agency_earning where month >= ? and month <= ? and type = ? and city like ?",
                (args["start_time"], args["end_time"], type, pattern))
            feePerType.append({
                "type": type,
                "fee": agency_earning[0]["fee_sum"]
            })
        start_year, start_month = np.array(
            args["start_time"].split("-")).astype(dtype=int).tolist()
        end_year, end_month = np.array(
            args["end_time"].split("-")).astype(dtype=int).tolist()
        start_year = int(start_year)
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if year == start_year and month < start_month:
                    continue
                if year == end_year and month > end_month:
                    continue
                now_month = str(year) + "-" + (str(month) if month > 9 else
                                               ("0" + str(month)))
                for type in range(1, 6):
                    data = query_db(
                        "select month, sum(finish_nums) as count, sum(earning_fee) as fee, type from agency_earning where month == ? and type = ? and city like ?",
                        (now_month, type, pattern))[0]

                    feePerMonth.append({
                        "type":
                        type,
                        "month":
                        now_month,
                        "fee":
                        data["fee"] if data["fee"] is not None else 0,
                        "count":
                        data["count"] if data["count"] is not None else 0
                    })
        user_data = query_db(
            "select username, city, level, sum(callup_fee + response_fee) as fee, count(*) as count from callup_success inner join user on callup_success.callup_user_id = user.id where finish_time >= ? and finish_time <= ? and city like ? group by callup_user_id ",
            (args["start_time"], args["end_time"], pattern))

        return {"month_data": feePerMonth, "type_fee": feePerType, "user_data":user_data}


class test_api(restful.Resource):
    @use_args({'id': fields.Integer(required=True)},
              location='json',
              unknown="EXCLUDE")
    def post(self, args):
        return {'id': args["id"]}


api.add_resource(HandleUserSignup, '/api/signup')
api.add_resource(CheckUserSignin, '/api/login')
api.add_resource(UpdateUserInfo, '/api/user/update_profile')
api.add_resource(GetUserList, '/api/admin/user_list')
api.add_resource(GetCallupList, '/api/request_list')

api.add_resource(AddResponse, '/api/user/add_response')
api.add_resource(UpdateResponse, '/api/user/update_response')
api.add_resource(ManageResponse, '/api/user/manage_response')

api.add_resource(AddRequest, '/api/user/add_request')
api.add_resource(UpdateCallUp, '/api/user/update_request')

api.add_resource(CallUpStastic, '/callupstastic')

api.add_resource(Statistic, '/api/admin/report')

api.add_resource(GetProfile, '/api/user/get_profile')

api.add_resource(CancelRequst, '/api/user/cancel_request')

api.add_resource(test_api, '/test')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='127.0.0.1', debug=True)
