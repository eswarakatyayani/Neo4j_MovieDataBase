from flask import Flask, Response, jsonify, request
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"  
username = "neo4j"
password = "g7ev_3eUHcbkWVINxW8-PY9f9QvvvOWCFh7Y2N5gREo"

driver = GraphDatabase.driver(uri, auth=(username, password))

app=Flask(__name__)


@app.route("/imdb", methods=['GET'])    #Display the data
def movies():
    session=driver.session()
    query=""" MATCH (m:Movie) RETURN m"""
    try:

        results= session.run(query)
        movies= []
        for record in results:
            node=record["m"]
            item=dict(node)
            movies.append(item)
        return jsonify(movies)

    except Exception as e:
        print("Exception ", e)
        response= Response("Search Records Error", status= 500, mimetype="application/json")
        return response

@app.route("/imdb", methods=['POST'])
def add_movies():
    data=request.get_json()
    print(data)
    session=driver.session()
    try:
        results= session.run("""UNWIND $actors AS a1
            UNWIND $g AS g1
            MERGE (m:Movie{ids:$id, title:$t, description:$d, year:$y,runtime:$rt, rating:$r,votes:$v})
            WITH *, trim(a1) as a2, trim(g1) as g2
            MERGE(:Person{name:a2})
            MERGE(:Person{name:$dir})
            MERGE(:Genres{type:g2})
            WITH *
            MATCH(m:Movie{ids:$id}), (p:Person{name:a2}), (d:Person{name:$dir}),(g:Genres{type:g2})
            MERGE (p)-[:ACTED_IN]->(m)
            MERGE (p)-[:DIRECTED]->(m)
            MERGE (m)-[:IN]->(g)
            RETURN m
            """,actors=data["actors"],id = data["Ids"],t=data["title"],d=data["description"],y=data["year"],rt=data["runtime"],r=data["rating"],v=data["votes"],a=data["actors"],dir=data["director"],g=data["genre"]
        )
 
        response= Response("New Record Added", status= 200, mimetype="application/json")
        return response  

    except Exception as e:
        print("Exception ", e)
        response= Response("Add Record Error", status= 500, mimetype="application/json")
        return response


@app.route("/imdb/<string:title>", methods=['PATCH'])
def update_movies(title):
    data=request.get_json()
    print(title)
    session=driver.session()
    try:
        results= session.run("""
        MATCH(m:Movie{title:$t}) SET m.description=$d, m.rating=$r
        """,t=title,d=data["description"],r=data["rating"],
        )
 
        response= Response("Record Updated", status= 200, mimetype="application/json")
        return response  

    except Exception as e:
        print("Exception ", e)
        response= Response("Update Record Error", status= 500, mimetype="application/json")
        return response

@app.route("/imdb/<string:title>", methods=['GET'])
def get_movies(title):

    session=driver.session()
    try:
        results= session.run("""MATCH (m:Movie{title:$t})  RETURN m""", t=title)
        movie = results.single()
        movie = dict(movie["m"])
        if movie is None:
            return Response("film " + title + " has not found",status=404,mimetype="application/json")
        # Get all the genres and attach to film
        query = """MATCH p=(Movie{title:$t})-[:IN]->(q:Genres) RETURN q.type"""
        genreResults= session.run(query, t=title)
        genres = []
        if genreResults:
            for g in genreResults:
                genres.append(g['q.type'])
         # Get all the actors and attach to film
        query = """MATCH m=(Movie{title:$t})<-[:ACTED_IN]-(p:Person) RETURN p.name"""
        actorResults= session.run(query, t=title)
        actors = []
        if actorResults:
            for g in actorResults:
                actors.append(g['p.name'])
        # Get the director and attach to film
        query = """MATCH m=(Movie{title:$t})<-[:DIRECTED]-(p:Person) RETURN p.name"""
        directorResults= session.run(query, t=title)
        director = ""
        if directorResults:
            director = directorResults.single()['p.name']
        print(genres)
        print(movie)
        movie["genres"] = genres
        movie["actors"] = actors
        movie["director"] = director
        #############
        return jsonify(movie)

    except Exception as e:
        print("Exception ", e)
        response= Response("Get Record Error", status= 500, mimetype="application/json")
        return response

@app.route("/imdb/<string:title>", methods=['DELETE'])      #Deleted the DataBase
def delete_movies(title):
    session=driver.session()
    try:
        results= session.run("""MATCH(m:Movie{title:$t}) DETACH DELETE m""",t=title)
        response= Response("Record Deleted", status= 200, mimetype="application/json")
        return response  

    except Exception as e:
        print("Exception ", e)
        response= Response("Record Deletion Error", status= 500, mimetype="application/json")
        return response



if __name__=="__main__":
    app.run(port=5000, debug=True)
