import falcon
import sqlite3
import ujson
import datetime
from envparse import Env

env = Env(DBNAME=str, TABLENAME=str)
env.read_envfile()

DBNAME = env('DBNAME')
TABLENAME = env('TABLENAME')


class AuthMiddleware(object):
    def process_request(self, req, resp):
        print(req)
        token = req.get_header('Authorization')
        account_id = req.get_header('Account-ID')

        challenges = ['Token type="Fernet"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token, account_id):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token, account_id):
        return True  # Suuuuuure it's valid...


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json')


class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = ujson.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = ujson.dumps(req.context['result'])


def make_query(query, data=None):
    with sqlite3.connect(DBNAME) as conn:
        c = conn.cursor()
        if data:
            cur = c.execute(query, data)
        else:
            cur = c.execute(query)
            r = cur.fetchall()
            print(r)
        if 'SELECT' in query:
            master_list = r
            return master_list
        else:
            conn.commit()
            return []


class Review:
    """Manage Review"""
    def on_get(self, req, res, tid=None):
        """for getting on or all the reviews
        """
        if tid:
            query = """SELECT * FROM %s where id=?""" % (TABLENAME)
            data = (tid,)
            response = make_query(query, data)
        else:
            query = """SELECT name, rating, review FROM %s""" % (TABLENAME)
            response = make_query(query)
        req.context['result'] = {'sucess': True, 'data': response, 'summary': 'List of data'}
        res.status = falcon.HTTP_200

    def on_post(self, req, res):
        data = req.context['doc']
        query = """INSERT INTO %s (name, email, rating, review, createdon) values(?, ?, ?, ?, ?)""" % (TABLENAME,)
        d = (data['name'], data['email'], data['rating'], data['review'], str(datetime.datetime.now()))
        make_query(query, d)
        req.context['result'] = {"sucess": True, "summary": "Thanks for submitting your review."}
        res.status = falcon.HTTP_200


review = Review()

app = falcon.API(middleware=[
    AuthMiddleware(),
    RequireJSON(),
    JSONTranslator(),
])

app.add_route('/api/v1/review/', review)
app.add_route('/api/v1/review/{tid}/', review)
