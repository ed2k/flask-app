from flask import jsonify
from flask import request


def html():
    return '''
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/brython/3.9.5/brython.min.js">
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/brython/3.9.5/brython_stdlib.min.js">
</script>
</head>
<body onload="brython()">
<div id="notes_taking"></div>
<div id='zone_kv'>kv list here</div>

<br>load from or save to localfile<br>
<input type="file" id="load_file">
<a id="save_file" href="#" download >save</a>
<br><textarea id="text_file" rows="5" cols="80"></textarea>

<br>test post to backend<br>
<textarea id='myinput'></textarea>
<div id='myoutput'></div>
<button id="myupdate">submit</button>

<br>entiry relation table for future AI training<br>
<div id='db_table'>db table here</div>
<script type="text/python">

from browser import document, html
from browser import ajax

url = "api/update"

def complete2(request):
    data = request.json
    document["myoutput"].text = data['data']

def click(event):
    headers = { 'Content-Type': 'application/json; charset=utf-8' };
    value = document['myinput'].value
    title = value.splitlines()[0]
    import javascript
    data = javascript.JSON.stringify(dict(doc=dict(title=title, body=value)))
    ajax.post(url, headers=headers, data=data, oncomplete=complete2)
    document["myoutput"].text = "waiting..."

document["myupdate"].bind("click", click)

# ------------------------
from browser import document, window
from browser.html import TABLE, TR, TD, INPUT, BUTTON, PRE, TEXTAREA

zone = document["zone_kv"]
search_kv = "status"
"""Test if the browser supports local storage"""
try:
    storage = window.localStorage
    storage.setItem("x", "x")
    storage.removeItem("x")
except:
    storage = None

from browser import bind
from browser.widgets.dialog import Dialog

def noteTakingWindow(ev):
    noteText = Dialog("Note", ok_cancel=True, left=0, top=0)
    noteText.panel <= html.DIV("" + TEXTAREA(cols=80, rows=10))

    # Event handler for "Ok" button
    @bind(noteText.ok_button, "click")
    def ok(ev):
        note = noteText.select_one("TEXTAREA").value
        print(note)
        noteText.close()
        key = note.splitlines()[0]
        value = storage.getItem(key)
        if value:
            note = note + value
        storage.setItem(key, note)
        show_kv()

btn = BUTTON('click me to start taking notes')
btn.bind('click', noteTakingWindow)
document['notes_taking'] <= btn

def action_kv_delete(ev):
    """User clicked on "remove" button"""
    button = ev.target
    row = button.closest("TR")
    key = row.get(selector="TD")[0].text
    if button.text == 'remove':
        storage.removeItem(key)
    else:
        value = storage.getItem(key)
        noteText = Dialog("Note update", ok_cancel=True, left=0, top=0)
        print([value])
        noteText.panel <= html.DIV(TEXTAREA(value, cols=80, rows=10))
        # value_field, scripts = markdown.mark(value)
        # noteText.panel.html = value_field

        # Event handler for "Ok" button
        @bind(noteText.ok_button, "click")
        def ok(ev):
            note = noteText.select_one("TEXTAREA").value
            noteText.close()
            storage.setItem(key, note)
            show_kv()
    # refresh table
    show_kv()

def action_kv_search(ev):
    """User clicked on "add" or "search" button"""
    global search_kv
    button = ev.target

    if button.text == 'Search':
        row = button.closest("TR")
        print('search', search_kv)
        search_kv = document['search_kv'].value
        search_kv = search_kv.strip()

    # refresh table
    show_kv()

from browser import markdown

def show_kv(*args):
    """Shows the data stored locally, add buttons to add / remove items"""
    zone.clear()

    if storage is None:
        zone <= "No local storage for this browser"
        return

    table = TABLE()

    btn_search = BUTTON("Search")
    btn_search.bind('click', action_kv_search)
    table <= TR(TD(INPUT(id='search_kv', value=search_kv)) +
        TD(btn_search))

    for i in range(storage.length):
        key = storage.key(i)
        value = storage.getItem(key)
        if len(search_kv) > 2 and (search_kv in value):
            print(value.find(key)+len(key)+1, key)
            value = value[value.find(key)+len(key)+1:]
            value_field = PRE(value, style=dict(width=600))
            # mk, scripts = markdown.mark(value)
            # value_field = DIV()
            # value_field.html = mk
            btn = BUTTON("remove")
            btn_update = BUTTON("update")
            btn.bind('click', action_kv_delete)
            btn_update.bind('click', action_kv_delete)
            table <= TR(TD(key) + TD(btn_update + btn))
            table <= TR(value_field)

    zone <= table



show_kv()

# ------------------------
# indexd DB for entity relationship graph
from browser import document, window, html
IDB = window.indexedDB
search_terms = {}

def create_db(*args):
      # The database did not previously exist, so create object stores and indexes.
      print('create db')
      db = dbreq.result
      store = db.createObjectStore("eb", {"keyPath": "eb"})
      entityIndex = store.createIndex("by_entity", "entity")
      relationIndex = store.createIndex("by_relation", "relation")
      print('db scrture')
      # Populate with initial data.
      store.put({"entity": "cap-backend", "relation": "down stream", "eb": "PCAP"})
      store.put({"entity": "cap-backend", "relation": "up stream", "eb": "hp-ep-mt"})


def btn_click(ev):
    """Generic callback function for buttons
    """
    global search_terms
    # The text on the button indicates the action: Add, Edit, Update or Delete
    action = ev.target.text

    # table row of the clicked button
    row = ev.target.parent.parent

    if action == "Delete":
        db = dbreq.result
        tx = db.transaction("eb", "readwrite")
        store = tx.objectStore("eb")
        cursor = store.delete(row.key)

        # when record is deleted, update table
        cursor.bind("success", show)

    elif action == "Add":
        values = [entry.value for entry in row.get(selector="INPUT")]
        data = dict(zip(['entity', 'relation', 'eb'], values))
        db = dbreq.result
        tx = db.transaction("eb", "readwrite")
        store = tx.objectStore("eb")
        if action == "Add":
            cursor = store.put(data)
        else:
            cursor = store.put(data, row.key)
        search_terms = data
        # when record is added, update table
        cursor.bind("success", show_db)

    elif action == "Edit":
        # Replace cells for "entity" and "author" by INPUT fields
        # Since isbn is he keyPath it can't be edited
        cells = row.get(selector="TD")
        for cell in cells[:-2]:
            value = cell.text
            cell.clear()
            cell <= html.INPUT(value=value)

        # Replace buttons "Edit" and "Delete" by button "Update"
        cells[-1].clear()
        update_btn = html.BUTTON("Update")
        cells[-1] <= update_btn

        # Bind its "click" event
        update_btn.bind("click", btn_click)

    elif action == "Update":
        values = [entry.value for entry in row.select("INPUT")]
        data = dict(zip(["entity", "relation"], values))
        data['eb'] = row.key # required for the "store.put" method below

        db = dbreq.result
        tx = db.transaction("eb", "readwrite")
        store = tx.objectStore("eb")
        cursor = store.put(data)

        # When record is updated, update table
        cursor.bind("success", show)
    elif action == 'Search':
        values = [entry.value for entry in row.get(selector="INPUT")]
        search_terms = dict(zip(['entity', 'relation', 'eb'], values))
        print('search', values, search_terms)
        db = dbreq.result
        tx = db.transaction("eb", "readonly")
        store = tx.objectStore("eb")
        cursor = store.openCursor()
        cursor.bind("success", show_db)

def show_db(ev):
    """Show the contents of store "eb" in a table"""
    print('show db')
    db = dbreq.result
    tx = db.transaction("eb", "readonly")
    store = tx.objectStore("eb")
    cursor = store.openCursor()

    # clear table
    document["db_table"].clear()

    # headers
    t = html.TABLE()
    document["db_table"] <= t

    t <= html.TR(html.TH(x) for x in ["Entity", "relation", "Entity", "Actions"])

    def add_row(ev):
        """Add a row to the table for each iteration on cursor
        When cursor in empty, add a line for new record insertion
        """
        res = ev.target.result
        if res:
            v = res.value
            toShow = False
            for key in ["entity", "relation", "eb"]:
                if search_terms.get(key) and search_terms[key] == getattr(v, key):
                    toShow = True
                    break
            if toShow:
                row = html.TR()
                row <= (html.TD(getattr(v, key))
                    for key in ["entity", "relation", "eb"])
                row <= html.TD(html.BUTTON("Edit")+
                    html.BUTTON("Delete"))
                row.key = res.key
                t <= row
            getattr(res, "continue")()
        else:
            # add empty row
            row = html.TR()
            row <= (html.TD(html.INPUT(name="new_%s" %key))
                for key in ["entity", "relation", "eb"])
            row <= html.TD(html.BUTTON("Add")+
                html.BUTTON("Search"))
            t <= row
            # bind all buttons
            for btn in t.get(selector="BUTTON"):
                btn.bind("click", btn_click)

    cursor.bind("success", add_row)


dbreq = IDB.open("library")

# If database doesn't exist, create it
dbreq.bind("upgradeneeded", create_db)

# Else print a table with all elements in table "books"
dbreq.bind("success", show_db)


#---------------------------------
def split_and_save(texts):
    buffer = []
    title = None
    rtn = chr(10)
    for line in texts.split(rtn):
        if line.strip() == '':
            # reset
            if title:
                value = rtn.join(buffer)
                if not buffer:
                    value = title
                storage.setItem(title, value)
            title = None
            buffer = []
            continue
        if title:
            buffer.append(line)
        else:
            title = line


from browser import bind, window, document

load_btn = document["load_file"]
save_btn = document["save_file"]

@bind(load_btn, "input")
def file_read(ev):

    def onload(event):
        """Triggered when file is read. The FileReader instance is
        event.target.
        The file content, as text, is the FileReader instance's "result"
        attribute."""
        document['text_file'].value = event.target.result
        # display "save" button
        save_btn.style.display = "inline"
        # set attribute "download" to file name
        save_btn.attrs["download"] = file.name
        split_and_save(event.target.result)

    # Get the selected file as a DOM File object
    file = load_btn.files[0]
    # Create a new DOM FileReader instance
    reader = window.FileReader.new()
    # Read the file content as text
    reader.readAsText(file)
    reader.bind("load", onload)

@bind(save_btn, "mousedown")
def save_button_mousedown(evt):
    """Create a "data URI" to set the downloaded file content
    Cf. https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
    """
    value = document['text_file'].value
    print(len(value), [value], window.history)
    if len(value) < 1:
        return
    content = window.encodeURIComponent(value)
    # set attribute "href" of save link
    save_btn.attrs["href"] = "data:text/plain," + content

</script>
</body>
'''


def query():
    cmd = request.args.get('cmd')
    print(cmd)
    import os
    stream = os.popen(cmd)
    output = stream.read()
    return jsonify(dict(data=output))


def update():
    from models import db_session, Article
    print(request.get_data())
    data = request.get_json(force=True)
    data = data['doc']
    title = data['title']
    row = db_session.query(Article).filter_by(title=title).first()
    if row:
        body = data['body']
        if row.body == body:
            return jsonify(dict(data={}))
        row.body = body
    else:
        article = Article()
        article.title = title
        article.body = data['body']
        db_session.add(article)
        data['createdAt'] = article.createdAt
    db_session.commit()
    return jsonify(dict(data=data))


'''
CREATE TABLE article (
    aid INTEGER NOT NULL,
    slug TEXT,
    title VARCHAR(200),
    body TEXT,
    tags TEXT,
    "createdAt" DATETIME NOT NULL,
    "updatedAt" DATETIME NOT NULL,
    PRIMARY KEY (aid)
);
'''
