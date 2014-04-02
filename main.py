# encoding: utf-8
import os
from random import sample

from flask import Flask, redirect, url_for, render_template, g, session, request
from flask_mail import Mail, Message

import sqlite3


app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RTMARIANA'
app.config.update(
    MAIL_SERVER = 'smtp.webfaction.com',
    MAIL_USERNAME = '',
    MAIL_PASSWORD = '',
    MAIL_DEFAULT_SENDER = 'contact@doingcast.com',
)
mail = Mail(app)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
DATABASE = os.path.join(SITE_ROOT, 'hal9000.db') 


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database  = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# / handler 
@app.route('/')
def index():
    #Exibir aqui a página inicial com as opções inglês e espanhol
    #Vou forçar o usuário a entrar na página inicial sempre que quiser começar uma sessão
    session['home'] = True
    return render_template('index.html', message = 'Hello MTF, your session is %s' % session['home'])


# /about handler
@app.route('/about')
def about():
    return render_template('about.html')


# /contact handler
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        msg = Message(
            recipients = ['contact@doingcast.com','ffreitasalves@gmail.com','roberto.cr@gmail.com','andre.mendesc@gmail.com'],
            subject = 'Practice Conversation Form',
            body = "name:%s\nemail:%s\nmsg:%s" %  (name,email,message),
            sender=('Practice Conversation',['contact@doingcast.com'])
            )
        mail.send(msg)
        msg = u'Your message has been sent!'

    return render_template('contact.html', msg=msg)


# /leave handler
@app.route('/leave', methods=['POST'])
def leave():
    if request.method == 'POST':
        room_id = request.form['room_id']

        #Diminui a população da sala ou exclui a sala, se ela ficar vazia
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        room =  cur.execute('SELECT * FROM rooms WHERE ID =  ?',[room_id]).fetchone()
        cur.close()
        
        if room:
            #Se a sala estiver vazia, deleta a sala:
            if room[2]-1:
                cur = con.cursor()
                cur.execute('UPDATE rooms SET POP = ? WHERE ID =  ?',(room[2]-1,room_id))
                con.commit()
                cur.close()
            else:
                cur = con.cursor()
                cur.execute('DELETE FROM rooms WHERE ID =  ?',[room_id])
                con.commit()
                cur.close()
        con.close()
    return 'True'


# /room handler
@app.route('/rooms/<language>')
def room(language):
    #Se ele não acessou a página inicial, tem que voltar pra lá
    if not session.get('home'):
        return redirect('/')

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    #Verifica as salas que tem menos de duas pessoas
    room = cur.execute('SELECT * FROM rooms WHERE POP < 2 AND LANGUAGE= ?', [language]).fetchall()    
    cur.close()
    if room:
        room = sample(room,1) [0]
        #Coloca o usuário em uma sala pré-existente
        room_id = room[0]
        cur = con.cursor()
        cur.execute('UPDATE rooms SET POP = ? WHERE ID=? and LANGUAGE = ?;', (room[2]+ 1, room_id, language))
        con.commit()
        cur.close()
    else:
        #Se não tem nenhuma sala desta língua com alguém esperando, então cria uma nova sala
        cur = con.cursor()
        new_room = cur.execute('INSERT INTO rooms(LANGUAGE, POP) VALUES(?,?);', (language,1))
        con.commit()
        room_id = new_room.lastrowid
        cur.close()

    con.close()
    return  render_template('room.html',language=language,room_id = room_id)


if __name__ == '__main__':
    app.run()

application = app