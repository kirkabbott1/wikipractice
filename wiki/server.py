from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from flask import Flask, render_template, request, redirect, session, flash
from wiki_linkify import wiki_linkify
import os
import markdown
import pg
import time
from time import localtime, strftime
db = pg.DB(
    dbname=os.environ.get('PG_DBNAME'),
    host=os.environ.get('PG_HOST'),
    user=os.environ.get('PG_USERNAME'),
    passwd=os.environ.get('PG_PASSWORD')
)

tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('Wiki', template_folder=tmp_dir)
app.secret_key = "wiki wiley kangarooSSS"

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']

    return redirect('/home')

@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    query = db.query("select * from a_user where username = $1", username)
    result_list = query.namedresult()
    if len(result_list) > 0:
        user = result_list[0]
        if user.password == password:
            # successfully logged in
            session['username'] = user.username
            return redirect('/allpages')
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/allpages')
def show_all():
    query = db.query("select * from page")
    query_result = query.namedresult()
    print query_result
    return render_template(
        'allpages.html',
        result = query_result
    )


@app.route('/<page_name>')
def display_page(page_name):
    query = db.query("select * from page where page_title = $1", page_name)
    result = query.namedresult()
    if len(result) < 1:
        return render_template(
            'placeholder.html',
            page_name=page_name
        )
    else:
        query2 = db.query("select page.page_title, content.timestamp, content.content, content.author from page, content where page.id = content.page_id and page.page_title = $1 order by timestamp DESC", page_name)
        result2 = query2.namedresult()
        # page_name = result2[0].page_title
        page_content = result2[0].content
        # print "PAGE CONTENT %r" % page_content
        wiki_content = markdown.markdown(wiki_linkify(page_content))
        author = result2[0].author
        # author = markdown.markdown(wiki_linkify(author))
        # print "string %r" % wiki_content
        return render_template(
            'pagename.html',
            page_name=page_name,
            content=wiki_content,
            page_content = page_content,
            author = author

        )
            # redirect('%s.html' % page_name)

@app.route('/<page_name>/edit')
def edit_page(page_name):
    query = db.query("select page.id, content.timestamp, content.author, content.content from page, content where page.id = content.page_id and page_title = $1 order by timestamp DESC", page_name)
    if 'username' not in session:
        return redirect('/login')
    else:
        # deny permisson
        # @app.route('/logout')
        # def logout():
        #     del session['username']
        #
        #     return redirect('/home')
        if len(query.namedresult()) > 0:
            resultid = query.namedresult()
            # print "OUR ID: %r" % resultid[0].id
            id = resultid[0].id
            author = resultid[0].author
            content = resultid[0].content

        else:
            id = ""
            author = ""
            content = ""
        return render_template(
            'edit.html',
            page_name=page_name,
            resultid = id,
            author = author,
            content = content
        )

@app.route('/<page_name>/save', methods=['POST'])
def add_entry(page_name):
    page_id = request.form.get('id')
    page_title = request.form.get('name')
    content = request.form.get('page_content')
    author = request.form.get('Author')
    query = db.query("select * from page where page_title = $1",page_name)
    # print "QUERY: %r" % query.namedresult()
    if 'username' not in session:
        return redirect('/login')
    else:

        if len(query.namedresult()) < 1:
            db.insert(
            'page', {
                    'page_title': page_name
                }

            )
            query = db.query("select page.id from page where page_title = $1", page_name)
            page_id = query.namedresult()[0].id
        else:
            pass
        db.insert(
        'content', {
                'content': content,
                'timestamp': time.strftime('%Y-%m-%d %I:%M:%S', localtime()),
                'page_id': page_id,
                'author': author
            }
        )
        flash("successfully updated %s" % page_name)
        return redirect('/%s' % page_name)

@app.route('/search', methods=['POST'])
def search():
    search = request.form.get('search')
    return redirect('/%s' % search)

@app.route('/<page_name>/history')
def history(page_name):
    query=db.query("select content.id, page.page_title, content.timestamp from page, content where page.id = content.page_id and page_title = $1 order by timestamp DESC", page_name)
    result = query.namedresult()
    return render_template(
        'history.html',
        page_name = page_name,
        result = result
    )
@app.route('/<page_name>/history/<content_id>')
def id(page_name,content_id):
    query=db.query("select * from content where id = $1", content_id)
    editedcontent = query.namedresult()[0]
    return render_template(
        'id.html',
        editedcontent = editedcontent
    )


if __name__ == '__main__':
    app.run(debug=True)
