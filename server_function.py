import json
import psycopg2

class ServerManager:
    def __init__(self):
        try:
            self.__db = psycopg2.connect(host='localhost', dbname='network', user='postgres',
                                         password='gg112828273', port='9131')
            self.__cursor = self.__db.cursor()
            print("DB connected!")
        except:
            raise ConnectionError

        self.num_member = self.__get_num_member()

    def __get_num_member(self):
        self.__cursor.execute("SELECT * FROM account")
        result = self.__cursor.fetchall()
        if result is not None:
            return len(result)
        else:
            return 0

    def _is_account_in_db(self, user_id):
        self.__cursor.execute("SELECT user_id FROM account WHERE user_id = '{}'".format(user_id))
        if self.__cursor.fetchone() is not None:
            return True
        else:
            return False

    def add_new_account(self, command):
        user_id, user_pw = command['user_id'], command['user_pw']
        # 새로운 계정 회원가입 신청
        if self._is_account_in_db(user_id):
            result = {
                'status_code': -1,
                'error': "이미 존재하는 ID입니다. 다른 ID를 선택해주세요."
            }
            str_json = json.dumps(result)
            return str_json
        else:
            try:
                self.__cursor.execute("INSERT INTO account (user_num_id, user_id, user_pw) VALUES ('{}', '{}', '{}')".format(self.num_member + 1, user_id, user_pw))
                self.__db.commit()
                result = {
                    'status_code': 1,
                    'success': "{} ID로 새로운 계정을 생성했습니다.".format(user_id)
                }
                print(result['success'])
                str_json = json.dumps(result)
                return str_json
            except:
                raise ConnectionError

    def __ok_to_login(self, id, pw):
        self.__cursor.execute("SELECT user_id FROM account WHERE user_id = '{}' and user_pw = '{}'".format(id, pw))
        if self.__cursor.fetchone() is not None: # id-pw 쌍이 같은 값이 존재하면
            return True
        else:
            return False


    def login(self, command):
        user_id, user_pw = command['user_id'], command['user_pw']
        if not self._is_account_in_db(user_id):  # 로그인 시도하는 ID가 DB에 없으면
            result = {
                'status_code': -1,
                'error': '존재하지 않는 계정이거나 비밀번호가 틀렸습니다. 다시 시도해주세요.'
            }
            str_json = json.dumps(result)
            return str_json
        else:  # 로그인 시도하는 ID가 DB에 존재하면
            if self.__ok_to_login(user_id, user_pw):
                # ID와 PW 모두 맞았을 때 + 로그인 테이블 만들기
                try:
                    self.__cursor.execute("SELECT user_num_id FROM account WHERE user_id = '{}'".format(user_id))
                    user_num_id = self.__cursor.fetchone()[0]
                    self.__cursor.execute("INSERT INTO login (user_num_id, user_id) VALUES ('{}', '{}')".format(user_num_id, user_id))
                    self.__db.commit()
                    result = {
                        'status_code': 1,
                        'user_id': user_id
                    }
                    str_json = json.dumps(result)
                    return str_json
                except:
                    raise ConnectionError
            else:
                # PW가 맞지 않는 경우
                result = {
                    'status_code': -1,
                    'error': '존재하지 않는 계정이거나 비밀번호가 틀렸습니다. 다시 시도해주세요.'
                }
                str_json = json.dumps(result)
                return str_json

    def __is_logined(self, user_id):
        try:
            self.__cursor.execute("SELECT * FROM login WHERE user_id = '{}'".format(user_id))
            query_result = self.__cursor.fetchone()
            if query_result is not None:  # 로그인 DB에 존재한다면
                return True
            else:
                return False
        except:
            raise ConnectionError


    def _get_follow_ids(self, user_id):
        self.__cursor.execute("SELECT follow_id FROM follow WHERE user_id = '{}'".format(user_id))
        following = [x[0] for x in self.__cursor.fetchall()]
        return following

    def return_posts(self, command):
        user_id = command['user_id']
        who_write = self._get_follow_ids(user_id)
        if who_write is None:
            who_write = [user_id]
        else:
            who_write.append(user_id)

        who_write_query = "'" + "','".join(who_write) + "'"
        self.__cursor.execute("SELECT user_id, texts FROM post WHERE user_id IN ({})".format(who_write_query))
        result_select = self.__cursor.fetchall()

        if len(result_select) == 0:
            result = {
                'status_code': -1, 'error': '자신 혹은 친구가 작성한 글이 없습니다.'
            }
            str_json = json.dumps(result)
            return str_json
        else:
            result = {
                'status_code': 1,
                'writers': [x[0] for x in result_select],
                'texts': [x[1] for x in result_select]
            }
            str_json = json.dumps(result)
            return str_json

    def _get_post_num(self):
        self.__cursor.execute("SELECT num FROM post_num")
        result = self.__cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            self.__cursor.execute("INSERT INTO post_num (num) VALUES('0')")
            self.__db.commit()
            return 0

    def _upload_post(self, user_id, text):
        post_num = self._get_post_num()
        self.__cursor.execute("INSERT INTO post (user_id, text_id, texts) VALUES ('{}', '{}', '{}')"
                              .format(user_id, post_num + 1, text))
        self.__cursor.execute("UPDATE post_num SET num = {}".format(post_num + 1))
        self.__db.commit()

    def write(self, command):
        user_id, text = command['user_id'], command['text']
        if not self.__is_logined(user_id):  # 로그인 확인
            result = {'status_code': -1, 'error': "로그인 되어 있지 않습니다"}
            str_json = json.dumps(result)
            return str_json
        else:
            try:
                self._upload_post(user_id, text)
                result = {'status_code': 1}
                str_json = json.dumps(result)
                return str_json
            except:
                result = {'status_code': -1, 'error': '게시물 업로드에 실패했습니다.'}
                str_json = json.dumps(result)
                return str_json


    def __is_followed(self, user_id, follow_id):
        # 이미 팔로우 되어있으면 True / 팔로우 안되어있으면 False
        self.__cursor.execute("SELECT * FROM follow WHERE user_id = '{}' and follow_id = '{}'".format(user_id, follow_id))
        if self.__cursor.fetchone() is not None:  # 팔로우 되어있으면
            return True
        else:
            return False


    def follow(self, command):
        user_id, follow_id = command['user_id'], command['follow_id']
        if not self.__is_logined(user_id):  # 로그인 확인
            result = {'status_code': -1, 'error': "로그인 되어 있지 않습니다"}
            str_json = json.dumps(result)
            return str_json

        if not self._is_account_in_db(follow_id):  # 팔로우 하려는 아이디가 회원이 아니라면?
            result = {'status_code': -1, 'error': "존재하지 않는 회원입니다".format(follow_id)}
            str_json = json.dumps(result)
            return str_json

        if not self.__is_followed(user_id, follow_id):  # 팔로우 안 된 상태라면?
            try:
                self.__cursor.execute("INSERT INTO follow (user_id, follow_id) VALUES ('{}', '{}')".format(user_id, follow_id))
                self.__db.commit()
                result = {'status_code': 1, 'success': "{}님을 Follow 했습니다.".format(follow_id)}
                str_json = json.dumps(result)
                return str_json
            except:
                raise ConnectionError

        else:  # 팔로우가 이미 된 상태라면?
            result = {'status_code': -1, 'error': "{}님은 이미 팔로우 된 회원입니다.".format(follow_id)}
            str_json = json.dumps(result)
            return str_json


    def get_follow_list(self, command):
        user_id = command['user_id']
        following = self._get_follow_ids(user_id)
        if len(following) == 0:  # following 없으면
            result = {'status_code': -1, 'error': 'following 한 사람이 없습니다.'}
            str_json = json.dumps(result)
            return str_json
        else:
            result = {'status_code': 1, 'friends': following}
            str_json = json.dumps(result)
            return str_json


    def logout(self, command):
        user_id = command['user_id']
        if self.__is_logined(user_id):  # 로그인 DB에 로그인 되어 있는 상태라면
            self.__cursor.execute("DELETE FROM login WHERE user_id = '{}'".format(user_id))
            self.__db.commit()
            result = {'status_code': 1}
            str_json = json.dumps(result)
            return str_json
        else:  # 로그인 DB에 로그인 되어 있지 않는 상태라면
            result = {'status_code': -1}
            str_json = json.dumps(result)
            return str_json


if __name__ == '__main__':
    """
    1. 회원가입 확인 코드
    sm = ServerManager()
    print(json.loads(sm.add_new_account({'user_id' : 'andy', 'user_pw' : '1234'})))
    
    2. 로그인 확인 코드
    sm = ServerManager()
    print(json.loads(sm.login({'user_id' : 'andy', 'user_pw' : '1234'})))
    
    3. 게시물 확인 코드
    sm = ServerManager()
    print(json.loads(sm.return_posts({'user_id' : 'andy'})))
    
    4. 게시물 업로드 확인 코드
    sm = ServerManager()
    print(json.loads(sm.write({'user_id' : 'andy', 'text' : '안녕하세요? 여러분! 모두들 반가워요!'})))
    
    5. 팔로우 확인 코드
    sm = ServerManager()
    print(json.loads(sm.follow({'user_id' : 'andy', 'follow_id' : 'lady'})))
    
    6. 팔로우 목록 확인 코드
    sm = ServerManager()
    print(json.loads(sm.get_follow_list({'user_id' : 'andy'})))
    
    7. 로그아웃 확인 코드
    sm = ServerManager()
    print(json.loads(sm.logout({'user_id' : 'andy'})))
    """

    sm = ServerManager()
    print(json.loads(sm.return_posts({'user_id': 'han'})))