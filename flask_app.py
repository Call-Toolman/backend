from flask import Flask, g, request
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs
import flask_cors
import flask_restful as restful
import sqlite3

DATABASE = 'database/callup_system.db'

app = Flask(__name__)
api = restful.Api(app)
# 允许跨域请求，因为后端是运行在5000端口上的，而前端是3000端口
flask_cors.CORS(app, supports_credentials=True)

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

    return {'result': 'success'}

    # 接收post请求上传的文件 test test
    # file = request.files.get('file')
    #
    # if file is None:
    #     # 表示没有发送文件
    #     print('failed')
    #     return "no file"
    #
    # # 直接使用上传的文件对象保存
    # print('received')
    # file.save("file")
    #
    # return "file received"



def query_db(query, args=(), onlyonerow=False):
    c = g.db.execute(query, args)
    rv = [dict((c.description[idx][0], value) for idx, value in enumerate(row)) for row in c.fetchall()]
    return (rv[0] if rv else None) if onlyonerow else rv


class HandleUserSignup(restful.Resource):
    @use_args({
        'username': fields.Str(required=True),
        'password': fields.Str(required=True),
        'phone_num': fields.Str(required=True),
        'description': fields.Str(required=True, allow_none=True),
        'real_name': fields.Str(required=True),
        'identity_type': fields.Integer(required=True),
        'identity_num': fields.Str(required=True),
        'city': fields.Str(required=True),
        'community': fields.Str(required=True)
    }, location='json')
    def post(self, args):
        userexist = query_db('select count(*) as count from user where username = ?', (args['username'],), onlyonerow=True)['count']
        if userexist == 1:
            return {'result': 'fail', 'errMsg': 'user name exist, change a name'}
        else:
            userNum = query_db('select count(*) as count from user', onlyonerow=True)['count']
            newID = userNum + 1
            userType = 1
            nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
            c = g.db.cursor()
            c.execute('insert into user (id, username, password, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, signup_time, modify_time, community) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (newID, args['username'], args['password'], args['phone_num'], args['description'], args['real_name'], userType, args['identity_type'], args['identity_num'], 1, args['city'], nowTime, nowTime, args['community']))
            g.db.commit() 
            return {'result': 'success'}


class CheckUserSignin(restful.Resource):
    @use_args({
        'username': fields.Str(required=True),
        'password': fields.Str(required=True)
    }, location='json')
    def get(self, args):
        userexist = query_db('select count(*) as count from user where username = ?', (args['username'],), onlyonerow=True)['count']
        if userexist == 1:
            rightpassword = query_db('select count(*) as count from user where username = ? and password = ?', (args['username'], args['password']), onlyonerow=True)['count']
            if rightpassword == 1:
                userinfo = query_db('select id, username, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user where username = ?', (args['username'],))
                return {'result': 'success', 'userinfo': userinfo}
            else:
                return {'result': 'fail', 'errMsg': 'wrong password'}
        else:
            return {'result': 'fail', 'errMsg': 'user not exist'}


class UpdateUserInfo(restful.Resource):
    @use_args({
        'username': fields.Str(required=True),
        'password': fields.Str(required=True, allow_none=True),
        'phone_num': fields.Str(required=True),
        'description': fields.Str(required=True, allow_none=True)
    }, location='json')
    def post(self, args):
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        if args['password']:
            c = g.db.cursor()
            c.execute('update user set password = ?, phone_num = ? , description = ? , modify_time = ? where username = ?', (args['password'], args['phone_num'], args['description'], nowTime, args['username']))
            g.db.commit()
        else:
            c = g.db.cursor()
            c.execute('update user set phone_num = ? , description = ? , modify_time = ? where username = ?', (args['phone_num'], args['description'], nowTime, args['username']))
            g.db.commit()
        
        userinfo = query_db('select id, username, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user where username = ?', (args['username'],))
        return {'result': 'success', 'userinfo': userinfo}


class GetUserList(restful.Resource):
    def get(self):
        userinfo = query_db('select id, username, phone_num, description, real_name, user_type, identity_type, identity_num, level, city, community from user')
        return {'result': 'success', 'userinfo': userinfo}


class AddCallUp(restful.Resource):
    @use_args({
        'username': fields.Str(required=True),
        'title': fields.Str(required=True),
        'type': fields.Str(required=True),
        'endtime': fields.Str(required=True),
        'description': fields.Str(required=True),
        'population': fields.Str(required=True),
        'img': fields.Str(required=True)
    }, location='json')

    def post(self, args):
        userID = str(query_db('select id from user where name = ?', (args['username'], ), onlyonerow=True)['id'])
        name = args['title']
        type = str(args['type'])
        description = args['description']
        member = str(args['population'])
        endTime = args['endtime']
        img = args['img']
        createTime = query_db('select date("now") as now', onlyonerow=True)['now']
        modifyTime = createTime
        state = str(2)

        print(userID, name, type, description, member, endTime, img, createTime, modifyTime, state)
        c = g.db.cursor()
        c.execute('''insert into callup (user_id,name,type,description,member,end_time,img,create_time,
        modify_time,state) values (?,?,?,?,?,?,?,?,?,?)''',
                  (userID, name, type, description, member, endTime, img, createTime, modifyTime, state))
        g.db.commit()
        return {'result': 'success'}


class ChangeCallUp(restful.Resource):
    @use_args({
        'id': fields.Str(required=True),
        'title': fields.Str(required=True),
        'type': fields.Str(required=True),
        'endtime': fields.Str(required=True),
        'description': fields.Str(required=True),
        'population': fields.Str(required=True),
        'img': fields.Str(required=True)
    }, location='json')

    def post(self, args):
        id = args['id']
        name = args['title']
        type = str(args['type'])
        description = args['description']
        member = str(args['population'])
        endTime = args['endtime']
        img = args['img']
        modifyTime = query_db('select date("now") as now', onlyonerow=True)['now']

        print(id, name, type, description, member, endTime, img, modifyTime)
        c = g.db.cursor()
        c.execute('''
            update callup 
            set name=?,type=?,description=?,member=?,end_time=?,img=?,modify_time=?
            where id=?''', (name, type, description, member, endTime, img, modifyTime, id))
        g.db.commit()
        return {'result': 'success'}


class GetCallupList(restful.Resource):
    def get(self):
        callupinfo = query_db('select callup.id as id, user.name as owner, user.id as owner_id, callup.name as name, callup.type as type, user.city as city, callup.description as description, callup.member as member, end_time, img, create_time as ctime, callup.modify_time as mtime, callup.state as state from user inner join callup on user.id = callup.user_id')
        for i in range(len(callupinfo)):
            callupinfo[i]['requests'] = query_db('select c.id as id, c.user_id as user_id, u.name as user_name, c.description as description, c.state as state from callup_response as c inner join user as u on c.user_id = u.id where callup_id = ?', (callupinfo[i]['id'],))

        return {'result': 'success', 'callupinfo': callupinfo}


class AddRequest(restful.Resource):
    @use_args({
        'id': fields.Integer(required=True),
        'user': fields.Str(required=True),
        'description': fields.Str(required=True)
    }, location='json')
    def post(self, args):
        print(args['description'])
        userID = query_db('select id from user where name = ?', (args['user'],), onlyonerow=True)['id']
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        c = g.db.cursor()
        c.execute("insert into callup_response (callup_id, user_id, description, create_time, modify_time, state) values (?, ?, ?, ?, ?, ?)", (args['id'], userID, args['description'], nowTime, nowTime, 1))
        g.db.commit()
        return {'result': 'success'}


class ChangeRequest(restful.Resource):
    @use_args({
        'id': fields.Integer(required=True),
        'description': fields.Str(required=True)
    }, location='json')
    def post(self, args):
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        c = g.db.cursor()
        c.execute("update callup_response set description = ? , modify_time = ? where id = ?", (args['description'], nowTime, args['id']))
        g.db.commit()
        return {'result': 'success'}


class ManageRequest(restful.Resource):
    @use_args({
        'id': fields.Integer(required=True),
        'state': fields.Integer(required=True)
    }, location='json')
    def post(self, args):
        c = g.db.cursor()
        c.execute("update callup_response set state = ? where id = ?", (args['state'], args['id']))
        g.db.commit()
        return {'result': 'success'}


class CallUpStastic(restful.Resource):
    @use_args({
        'month': fields.Str(required=True)
    }, location='query')
    def get(self, args):
        profit = {}
        if args['month'] == "all":
            c = g.db.cursor()
            for i in range(1,6):
                c.execute("select sum(4*member) as sum from callup where state = 1 and type = ?", (str(i)))
                temp = [dict((c.description[idx][0], value) for idx, value in enumerate(row)) for row in c.fetchall()][0]['sum']
                profit[i] = temp if temp else 0
            g.db.commit()
        else:
            c = g.db.cursor()
            for i in range(1,6):
                c.execute("select sum(4*member)  as sum from callup where state = 1 and type = ? and end_time like ?", (str(i), args['month']))
                temp = [dict((c.description[idx][0], value) for idx, value in enumerate(row)) for row in c.fetchall()][0]['sum']
                profit[i] = temp if temp else 0
            g.db.commit()
        return {'result': 'success', 'profit': profit}

class test_api(restful.Resource):
    @use_args({
        'id':fields.Integer(required=True)
    },location='json')
    def post(self, args):
        return {'id':args["id"]}

api.add_resource(HandleUserSignup, '/api/signup')
api.add_resource(CheckUserSignin, '/api/login')
api.add_resource(UpdateUserInfo, '/api/user/update_info')
api.add_resource(GetUserList, '/api/admin/user_list')
api.add_resource(GetCallupList, '/calluplist')

api.add_resource(AddRequest, '/addreq')
api.add_resource(ChangeRequest, '/changereq')
api.add_resource(ManageRequest, '/managereq')

api.add_resource(AddCallUp, '/addcallup')
api.add_resource(ChangeCallUp, '/changecallup')

api.add_resource(CallUpStastic, '/callupstastic')

api.add_resource(test_api, '/test')



if __name__ == '__main__':
  app.run(host='127.0.0.1', debug=True)



