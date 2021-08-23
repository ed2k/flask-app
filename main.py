from flask import Flask
#from flask_graphql import GraphQLView
#from models import db_session
#from schema import schema, Department
from flask_cors import CORS
from flask import request, jsonify
from models import User, db_session, Article, Tags

app = Flask(__name__)
app.debug = True
#cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
CORS(app)


@app.route('/api/users', methods=('POST',))
def register_user():
    print(request.get_data())
    data = request.get_json(force=True)
    username = data['username']
    email = data['email']
    password = data['password']

    u = User()
    u.username = username
    u.email = email
    u.password = password
    u.token = username + ":" + email + ':' + password
    db_session.add(u)
    db_session.commit()

    del data['password'] 
    data['token'] = u.token
    return jsonify(dict(user=data))

@app.route('/api/users/login', methods=('POST',))
def login_user():
    print(request.get_data())
    data = request.get_json(force=True)
    data = data['user']
    email = data['email']
    password = data['password']
    user = db_session.query(User).filter_by(email=email).first()
    if user is not None and user.check_password(password):
        username = user.username
        user.token = username + ":" + email + ':' + password
        db_session.commit()
        data['username'] = username
        data['token'] = user.token
        return jsonify(dict(user=data))
    return 'user not found', 404

@app.route('/api/tags', methods=('GET',))
def api_tags():
    print(request.get_data())
    return {}

@app.route('/api/articles', methods=('GET',))
def api_articles():
    print(request.get_data())
    return {}

@app.route('/api/articles', methods=('POST',))
def make_article():
    print(request.get_data())
    print(request.headers.get('Authorization'))
    aid = request.headers.get('Authorization', 'a anony').split()[1].split(':')[0]
    # user = db_session.query(User).filter_by(username=aid).first()
    # if not user:
    #     return "user not found", 404
    data = request.get_json(force=True)
    data = data['article']
    article = Article()
    article.title = data['title']
    article.body = data['body']
    # body, title, tagList=None

    tagList = data.get('tagList')
    if tagList is not None:
        for tag in tagList:
            mtag = db_session.query(Tags).filter_by(tagname=tag).first()
            if not mtag:
                mtag = Tags()
                mtag.tagname = tag
                db_session.add(mtag)
            article.add_tag(mtag)
    db_session.add(article)
    db_session.commit()
    data['createdAt'] = article.createdAt
    return jsonify(dict(article=data))


# app.add_url_rule(
#     '/graphql',
#     view_func=GraphQLView.as_view(
#         'graphql',
#         schema=schema,
#         graphiql=True # for having the GraphiQL interface
#     )
# )

@app.route('/', methods=('GET',))
def load_apprun():
    return '''
<html>

<head>
    <meta charset="utf-8">
    <script type="text/javascript"
        src="https://cdn.jsdelivr.net/npm/brython@3.9.5/brython.min.js">
    </script>
</head>
<body onload="brython()">
<script type="text/typescript">
// Async fetch
const state = {};
const view = state => <>
  <div><button $onclick="fetchComic">fetch ...</button></div>
  {state.loading && <div>loading ... </div>}
  {state.comic && <div> {state.comic.token}</div>}
</>;
const update = {
  'loading': (state, loading) => ({...state, loading }),
  'fetchComic': async _ => {
    app.run('loading', true);
    const headers = { 'Content-Type': 'application/json; charset=utf-8' };
    const body = {
      'email': 'sunyin51@gmail.com', 'password':'GodZilla'
    };
    const response = await fetch('http://localhost:5000/api/user/login', {
      'method':'POST',
      headers,
      body: body && JSON.stringify(body)  
    });
    const comic = await response.json();
    return {comic};
  }
};
function apprunOnload() {
    app.start(document.body, state, view, update);
}

</script>
<script type="text/python">
from browser import document, ajax

url = "http://localhost:5000/api/user/login"
msg = "Position of the International Space Station at {}: {}"

def complete(request):
    data = request.json
    token = data["token"]
    document["zone10"].text = token

def click(event):
    headers = { 'Content-Type': 'application/json; charset=utf-8' };
    data = {
      'email': 'sunyin51@gmail.com', 'password':'GodZilla'
    }
    ajax.post(url, headers=headers, data=data, oncomplete=complete)
    document["zone10"].text = "waiting..."

document["button10"].bind("click", click)

</script>
<button id="button10">submit</button>
<div id="zone10"></div>

</body>
'''


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
