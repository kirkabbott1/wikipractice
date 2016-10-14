from flask import Flask, render_template, request, redirect
import pg

db = pg.DB(dbname='music_db')

app = Flask('albumApp')


@app.route('/album/<int:album_id>')
def album_info(album_id):
    query = db.query('''
    select
        album.id,
        album.name,
        album.released
    from
        album
    where album.id = %d
    ''' % album_id)
    result_list = query.namedresult()
    album = result_list[0]
    return render_template(
        'album_info.html',
        album=album
    )

if __name__ == '__main__':
    app.run(debug=True)
