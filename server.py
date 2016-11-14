from flask import Flask, render_template, request, redirect
from wiki_linkify import wiki_linkify
import markdown
import pg
db = pg.DB(dbname='wiki_db')

app = Flask('wikiApp')

@app.route('/<page_name>')
def display_page(page_name):
    query = db.query("select * from page where page_title = '%s'" % page_name)
    result = query.namedresult()
    if len(result) < 1:
        return render_template(
            'placeholder.html',
            page_name=page_name
        )
    else:
        query2 = db.query("select * from page where page_title = '%s'" % page_name)
        result2 = query2.namedresult()
        # page_name = result2[0].page_title
        page_content = result2[0].content
        print "PAGE CONTENT %r" % page_content
        wiki_content = markdown.markdown(wiki_linkify(page_content))
        author = result2[0].author
        author = markdown.markdown(wiki_linkify(author))
        print "string %r" % wiki_content
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
    query = db.query("select id from page where page_title = '%s'" % page_name)
    if len(query.namedresult()) > 0:
        resultid = query.namedresult()
        print "OUR ID: %r" % resultid[0].id
        id = resultid[0].id
    else:
        id = ""
    return render_template(
    'edit.html',
    page_name=page_name,
    resultid = id
    )

@app.route('/<page_name>/save', methods=['POST'])
def add_entry(page_name):
    resultid = request.form.get('id')
    print "OUR ID: %r" % resultid
    page_title = request.form.get('name')
    content = request.form.get('page_content')
    author = request.form.get('Author')
    query = db.query("select * from page where page_title = '%s'" % page_name)
    print "QUERY: %r" % query.namedresult()
    if len(query.namedresult()) < 1:
        db.insert(
        'page', {
                'page_title': page_name,
                'author': author,
                'content': content
            }
        )
    else:
        db.update(
        'page', {
                'id': resultid,
                'page_title': page_name,
                'author': author,
                'content': content
            }
        )
    return redirect('/%s' % page_name)

# @app.route('/')
# def camel(word):
#     return wiki_linkify(word)

if __name__ == '__main__':
    app.run(debug=True)
