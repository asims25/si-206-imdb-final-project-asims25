# si-206-imdb-final-project-asims25

# Final Project Explanation

My Project involved scraping and crawling multiple links in order to create a
comprehensive database of recent and old movies.

I first scraped the wikipedia table to collect data on every movie that has
ever won an Oscar. I collected the movie names, number of Oscar nominations,
and number of Oscars won.

I then scraped and crawled through 2 links from the Imdb website. The first
link contained information on 1000 movies that are now on DVD and the second
link contained information on movies that have come out in the past year. From
all this data I created a massive nested dictionary with the movie names as
keys and a dictionary of datatypes(genre, release year, director, etc.) as the
value.I then created a database of two tables: Movie_Information and
Movie_Reviews.

#Command Line Help

I then created a interactive part that queries data from this database. You can
access two types of information in the command line. If you enter 'info all
info <movie name>' into the command line, then all the data about that movie
is printed in terminal. If you enter 'info <datatype> <movie name>' then only
that specified datatype for that specified movie will be returned. There is
also the visual option. If you enter 'graph reviews <release year>' then a  
double bar graph of the top 20 rated movies for that specified year will be
displayed. If you enter 'graph boxoffice <release year>' then a scatterplot
displaying the top 20 grossing movies for that specified year will be displayed.
If you enter 'graph genre 2017' then a bar graph showing the number of movies
in each genre that were made in that specified year will be displayed. If
'graph oscars' is entered into the command line than a double bar graph
displaying the number of Oscar nominations and the number of Oscars won will
be displayed. The top 20 movies based on the number of Oscar nominations will
be displayed.
