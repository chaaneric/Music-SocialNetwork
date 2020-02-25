from app import db
from app.models import Album, Song, Artist
import xml.etree.ElementTree as ET

fields_needed = ["Name", "Artist", "Album", "Genre"]


def populate_songs():
	tree = ET.parse("Library.xml")
	root = tree.getroot()[0][17]

	songs = root.findall('dict')

	for song in songs:
		current_song = {"Name": "Unknown", "Artist": "Unknown", "Album": "Unknown", "Genre": "Unknown"}
		for i in range(0, len(song), 2):
			if song[i].text in fields_needed:
				current_song[song[i].text] = song[i+1].text



		art = Artist.query.filter_by(name=current_song["Artist"]).first()
		a = Album.query.filter_by(name=current_song["Album"]).first()
		if art == None:
			art = Artist(name=current_song["Artist"])
			db.session.add(art)
			db.session.commit()


		if a == None:
			a = Album(name=current_song["Album"], genre=current_song["Genre"], artist=art)
			db.session.add(a)
			db.session.commit()


		s = Song(name=current_song["Name"], album=a)

		db.session.add(s)
		db.session.commit()


if __name__ == '__main__':
    populate_songs()



