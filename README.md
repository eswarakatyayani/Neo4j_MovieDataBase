PERFORMING CURD OPERATIONS

1.	Insert the new movie information.
   Create new movie information
@app.route('/imdb', methods=['POST'])

2.	Update the movie information using title. (By update only title, description, and rating)
   Update New details for old one
@app.route('/imdb/<string:fname>', methods=['PATCH'])

3.	Retrieve all the movies in database.
    Display all details
@app.route('/imdb', methods=['GET'])

4.	Delete the movie information using title.
   Delete the data
@app.route('/imdb/<string:fname>', methods=['DELETE'])

5.	Display the movie’s details includes actors, directors and genres using title.
    Display Actor,director,genre using title
@app.route('/imdb/<string:fname>', methods=['GET'])

