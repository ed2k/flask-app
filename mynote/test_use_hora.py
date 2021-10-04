from flask import Flask

from flask_cors import CORS
from flask import request, jsonify

import tensorflow_hub as hub
from absl import logging
import numpy as np
from horapy import HNSWIndex

app = Flask(__name__)
app.debug = True

CORS(app)

knowledge_dict = dict()
NEWLINE = '\n'
dimension = 512
index = HNSWIndex(dimension, "usize")

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)
print ("module %s loaded" % module_url)
def embed(input):
  return model(input)


def convert_one_file(filename):
    """prefix list of keywords
    """
    buffer = list()
    progress = 0
    for line in open(filename):
        if line.strip() == '':
            if buffer:
                progress += 1
                message = ''.join(buffer)
                # print(buffer)
                message_embeddings = embed([message])
                message_embedding = np.array(message_embeddings).tolist()[0]
                # print(message_embedding)
                message_embedding_snippet = ", ".join((str(x) for x in message_embedding))
                knowledge_dict[progress] = message
                index.add(np.float32(message_embedding), progress)
                buffer =  list()
                if progress % 10000 == 1:
                    print(progress)
        else:
            buffer.append(line)

convert_one_file('/home/a/knowledge/test.txt')
print('build index')
index.build("euclidean")  # build index
print('done')
            

@app.route('/api/q/<query>',  methods=('GET',))
def api_query(query):
    #query = request.args.get('q')
    print(query)
    message_embeddings = embed([query])
    message_embedding = np.array(message_embeddings).tolist()[0]

    results = index.search(message_embedding, 10)
    r = list()
    for i in results:
        r.append(knowledge_dict[i])
    return jsonify(dict(data=r))


@app.route('/', methods=('GET',))
def load_apprun():
    return '''
    <script type="text/javascript"
        src="https://cdn.jsdelivr.net/npm/brython@3.9.5/brython.min.js">
    </script>

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
      'email': 's@g.com', 'password':'geez'
    }
    ajax.post(url, headers=headers, data=data, oncomplete=complete)
    document["zone10"].text = "waiting..."

document["button10"].bind("click", click)

</script>
<button id="button10">submit</button>
<div id="zone10"></div>

</body>
'''

if __name__ == '__main__':
    app.run(host="0.0.0.0")
