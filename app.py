# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, send_file
from markupsafe import escape
import json
import requests
import mysql.connector
import random as rd

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)


mydb = mysql.connector.connect(
    host="YOUR-HOST",
    user="YOUR-USER",
    passwd="YOUR-PASWORD",
    database="YOUR-DATABASE"
)


def animeRequestSQLAll(id):
    mycursor = mydb.cursor()
    mycursor.execute(f"""
    SELECT 
	Anime.id_anime,
	Anime.nom_anime,
	Anime.url_img_anime,
	Anime.nbepisode_anime,
	Anime.vue_anime,
	Anime.desc_anime,
	Format.nom_format,
	Statue.state_statue,
        alternative_titles_en_anime,
        alternative_titles_ja_anime,
        alternative_titles_synonyms_anime
    FROM 
	Anime, 
	Format,
	Statue
    WHERE 
	Anime.format_id_format = Format.id_format and
	Anime.statue_id_statue = Statue.id_statue and  
        Anime.id_anime = {id}
    """)
    return mycursor.fetchall()


def animeRequestSQL(offset, limit):
    mycursor = mydb.cursor()
    mycursor.execute(f"""
    SELECT 
	Anime.id_anime,
        Anime.nom_anime,
        Anime.url_img_anime,
	Anime.nbepisode_anime,
        Anime.vue_anime,
        Anime.desc_anime, 
        Format.nom_format 
    FROM 
	Anime, 
        Format 
    WHERE 
	    Anime.format_id_format = Format.id_format
    ORDER BY 
	    Anime.id_anime
    LIMIT {limit} 
    OFFSET {offset};
    """)
    return mycursor.fetchall()


def animeRequestSQLSearch():
    mycursor = mydb.cursor()
    mycursor.execute(f"""
    SELECT 
	Anime.id_anime,
        Anime.nom_anime,
        Anime.url_img_anime,
	Anime.nbepisode_anime,
        Anime.vue_anime,
        Anime.desc_anime, 
        Format.nom_format 
    FROM 
	Anime, 
        Format 
    WHERE 
	    Anime.format_id_format = Format.id_format
    ORDER BY 
	    Anime.id_anime;
    """)
    return mycursor.fetchall()


def DataFormat(v):
    return {"id": v[0], "name": v[1], "img": v[2],
            "nbep": v[3], "vue": v[4], "desc": v[5], "type": v[6]}


def DataFormatDetail(v):
    return {"id": v[0], "name": v[1], "img": v[2],
            "nbep": v[3], "vue": v[4], "desc": v[5], "type": v[6], "statue": v[7], "en": v[8], "ja": [9], "syn": v[10].split(";")}


@app.route('/api/anime', methods=['GET'])
def anime():
    id = request.args.get('id', default=rd.randint(0, 42000))
    try:
        id = int(id)
        data = animeRequestSQLAll(id)[0]
        data = DataFormatDetail(data)
    except:
        data = None

    return jsonify({'status': '200', 'animes': data})


@app.route('/api/page', methods=['GET'])
def page():
    offset = request.args.get('offset', default=0)
    limit = request.args.get('limit', default=1)
    data = animeRequestSQL(offset, limit)
    for k, v in enumerate(data):
        data[k] = DataFormat(v)
    return jsonify({'status': '200', 'animes': data})


@app.route('/api/search', methods=['GET'])
def search():
    title = request.args.get('title', default=None)
    if title != None:
        title = title.lower().split(' ')
        TMPdata = animeRequestSQLSearch()
    else:
        TMPdata = animeRequestSQL(rd.randint(0, 40000), 10)
    data = []
    for k, v in enumerate(TMPdata):
        continuer = True
        if title != None:
            for i in title:
                if i in v[1].lower():
                    pass
                else:
                    continuer = False
        if continuer:
            data.append(DataFormat(v))
    return jsonify({'status': '200', 'search': title, 'animes': data})


@app.route('/return-files/')
def return_files_tut():
    try:
        return send_file('./data.db', attachment_filename='data.db')
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
