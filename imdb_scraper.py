import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from pprint import pprint
import plotly.plotly as py
import plotly.graph_objs as go

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params= {}, auth = None):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        cach_str='Getting data from cache.....'
        print(cach_str.upper())
        return CACHE_DICTION[unique_ident]
    else:
        request_str='Making new request.....'
        print(request_str.upper())
        resp = requests.get(baseurl, params, auth=auth)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]
#---------------------------------------------------------------------------------------------
#will scrape wikipedia page that contains a list of movies that has won an oscar
#returns a dictionary with movies as keys and the amount of oscars won as dictionaries
#Note: Competitive Oscars are separated from non-competitive Oscars (i.e. Honorary Award, Special Achievement Award, Juvenile Award); as such, any films that were awarded a non-competitive award will be shown in brackets next to the number of competitive wins.
best_picture_dictionary={}
best_picture_list=[]
baseurl = 'https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films'
page_text = make_request_using_cache(baseurl)
page_soup = BeautifulSoup(page_text, 'html.parser')
content_div=page_soup.find('div', id='mw-content-text')
table_rows=content_div.find_all('tr')
for row in table_rows:
    table_data=row.find_all('td')
    if len(table_data)==4:
        movie_name=table_data[0].text.strip()
        movie_year=table_data[1].text.strip()
        best_picture_list.append(movie_name)
        oscar_awards=table_data[2].text.strip()
        oscar_noms=table_data[3].text.strip()
        best_picture_dictionary[movie_name]={}
        best_picture_dictionary[movie_name]['OscarNoms']=oscar_noms
        best_picture_dictionary[movie_name]['OscarsWon']=oscar_awards
#function will scrape the DVD home page
#return dictionary of all the data scraped from each movie
def get_dvd_movie(page):
    dvd_movie_dict={}
    baseurl = 'https://www.imdb.com/list/ls006625188/'
    added_url='?sort=list_order,asc&st_dt=&mode=detail&page='
    if page > 0:
        baseurl=baseurl+added_url+str(page)
    request = make_request_using_cache(baseurl)
    soup = BeautifulSoup(request, "html.parser")
    content_div=soup.find('div', class_='article listo')
    each_movie=content_div.find_all('div', class_='lister-item-content')
    for movie in each_movie:
        for x in movie.find_all('h3', class_='lister-item-header'):
            movie_name=x.find('a').text.strip()
            movie_year=x.find('span', class_='lister-item-year text-muted unbold').text.strip()
            for y in movie_year:
                if y.isdigit()==False:
                    movie_year=movie_year.strip(y)
        movie_genre=movie.find('span', class_='genre').text.strip()
        try:
            movie_rating=movie.find('span', class_='certificate').text.strip()
        except:
            movie_rating='NA'#for older movies without this datatype
        runtime=movie.find('span', class_='runtime').text.strip()
        plot=movie.find('p', class_="").text.strip()
        for x in movie.find_all('div', class_='inline-block ratings-imdb-rating'):
            movie_review=x.find('strong').text.strip()
        for x in movie.find_all('div', class_='inline-block ratings-metascore'):
            try:
                metascore_data=x.find(class_='metascore')
                metascore=metascore_data.text.strip()
            except:
                metascore='NA'#for older movies without this datatype
        for x in movie.find_all('p', class_='text-muted text-small')[2]:
            box_office_data=x.string
            if box_office_data!=None:
                if '$' in box_office_data:
                    box_office=box_office_data
        people_list=[]
        director_list=[]
        actor_list=[]
        for x in movie.find_all('p', class_='text-muted text-small')[1]:
            people_data=x.string.strip()
            split_people=people_data.split('|')
            for x in split_people:
                if x!=',':
                    if len(x.split())!=0:
                        people=x
                        people_list.append(people)
        if len(people_list)>0:
            if people_list[0]=='Director:':
                director_list.append(people_list[1])
                actor_list.append(people_list[3])
            elif people_list[0]=='Directors:':
                director_list.append(people_list[1])
                actor_list.append(people_list[4])
                if actor_list[0]=='Stars:':
                    actor_list[0]=people_list[5]
        for x in director_list:
            director=x
        for x in actor_list:
            star=x
        dvd_movie_dict[movie_name]={}
        dvd_movie_dict[movie_name]['Plot']=plot
        dvd_movie_dict[movie_name]['ReleaseYear']=movie_year
        dvd_movie_dict[movie_name]['Genre']=movie_genre
        dvd_movie_dict[movie_name]['Rating']=movie_rating
        dvd_movie_dict[movie_name]['Runtime']=runtime
        dvd_movie_dict[movie_name]['UserReview']=movie_review
        try:
            dvd_movie_dict[movie_name]['BoxOffice']=box_office
        except:
            dvd_movie_dict[movie_name]['BoxOffice']='Not released'
        dvd_movie_dict[movie_name]['Metascore']=metascore
        dvd_movie_dict[movie_name]['Director']=director
        dvd_movie_dict[movie_name]['Star']=star
        if movie_name in best_picture_list:
            oscar_noms=best_picture_dictionary[movie_name]['OscarNoms']
            oscar_awards=best_picture_dictionary[movie_name]['OscarsWon']
            dvd_movie_dict[movie_name]['OscarNominations']=oscar_noms
            dvd_movie_dict[movie_name]['OscarsWon']=oscar_awards
        else:
            dvd_movie_dict[movie_name]['OscarNominations']='None'
            dvd_movie_dict[movie_name]['OscarsWon']='None'
    return dvd_movie_dict
#function will scrape recent and upcoming movies
#return a dictionary of data for all those movies
def scrape_recent_and_upcoming_movies(page):
    recent_movie_dict={}
    baseurl = 'https://www.imdb.com/list/ls031297486/'
    added_url='?sort=list_order,asc&st_dt=&mode=detail&page='
    if page > 0:
        baseurl=baseurl+added_url+str(page)
    request = make_request_using_cache(baseurl)
    soup = BeautifulSoup(request, "html.parser")
    content_div=soup.find('div', class_='article listo')
    each_movie=content_div.find_all('div', class_='lister-item-content')
    for movie in each_movie:
        for x in movie.find_all('h3', class_='lister-item-header'):
            movie_name=x.find('a').text.strip()
            movie_year=x.find('span', class_='lister-item-year text-muted unbold').text.strip()
            for y in movie_year:
                if y.isdigit()==False:
                    movie_year=movie_year.strip(y)
        movie_genre=movie.find('span', class_='genre').text.strip()
        try:
            movie_rating=movie.find('span', class_='certificate').text.strip()
            runtime=movie.find('span', class_='runtime').text.strip()
        except:
            movie_rating='Not released'#For upcoming movies with less infomration
            runtime='Not released'#For upcoming movies with less infomration
        plot=movie.find('p', class_="").text.strip()
        for x in movie.find_all('div', class_='inline-block ratings-imdb-rating'):
            movie_review=x.find('strong').text.strip()
            if movie_review!=None:
                movie_review=movie_review
            else:
                movie_review='Not Released'
        for x in movie.find_all('div', class_='inline-block ratings-metascore'):
            metascore_data=x.find(class_='metascore')
            metascore=metascore_data.text.strip()
            if metascore.isdigit()==True:
                metascore=metascore
            else:
                metascore='Not Released'
        for x in movie.find_all('span'):
            box_office_data=x.string
            if box_office_data!=None:
                if '$' in box_office_data:
                    box_office=box_office_data
                else:
                    box_office='Not released' #For upcoming movies with less infomration
        people_list=[]
        director_list=[]
        actor_list=[]
        for x in movie.find_all('p', class_='text-muted text-small')[1]:
            people_data=x.string.strip()
            split_people=people_data.split('|')
            for x in split_people:
                if x!=',':
                    if len(x.split())!=0:
                        people=x
                        people_list.append(people)
        if len(people_list)>0 and movie_year=='2017':
            if people_list[0]=='Director:':
                director_list.append(people_list[1])
                actor_list.append(people_list[3])
            elif people_list[0]=='Directors:':
                director_list.append(people_list[1])
                actor_list.append(people_list[4])
                if actor_list[0]=='Stars:':
                    actor_list[0]=people_list[5]
        for x in director_list:
            director=x
        for x in actor_list:
            star=x
        if movie_year=='2017':
            recent_movie_dict[movie_name]={}
            recent_movie_dict[movie_name]['Plot']=plot
            recent_movie_dict[movie_name]['ReleaseYear']=movie_year
            recent_movie_dict[movie_name]['Genre']=movie_genre
            recent_movie_dict[movie_name]['Rating']=movie_rating
            recent_movie_dict[movie_name]['Runtime']=runtime
            recent_movie_dict[movie_name]['UserReview']=movie_review
            try:
                recent_movie_dict[movie_name]['Metascore']=metascore
            except:
                recent_movie_dict[movie_name]['Metascore']='Not released'
            recent_movie_dict[movie_name]['BoxOffice']=box_office
            recent_movie_dict[movie_name]['Director']=director
            recent_movie_dict[movie_name]['Star']=star
            if movie_name in best_picture_list:
                recent_movie_dict[movie_name]['OscarNominations']=oscar_noms
                recent_movie_dict[movie_name]['OscarsWon']=oscar_awards
            else:
                recent_movie_dict[movie_name]['OscarNominations']='None'
                recent_movie_dict[movie_name]['OscarsWon']='None'
    return recent_movie_dict

final_movie_dict = {}
for i in range(12):
    dvd_movie_dict = get_dvd_movie(i)
    final_movie_dict.update(dvd_movie_dict)
for i in range(3):
    recent_movie_dict = scrape_recent_and_upcoming_movies(i)
    final_movie_dict.update(recent_movie_dict)
# pprint(final_movie_dict)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DBNAME='movie_info.db'
def init_db():
    try:
        conn=sqlite3.connect(DBNAME)
        cur=conn.cursor()
    except:
        print('No connection!')

    statement = '''
        DROP TABLE IF EXISTS 'Movie_Reviews';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Movie_Information';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Movie_Reviews' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'CriticImdbScore' REAL,
            'UserImdbScore' REAL,
            'BoxOfficeMoney' INTEGER
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Movie_Information' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'MovieName' TEXT NOT NULL,
            'ReleaseYear' TEXT NOT NULL,
            'Genre' TEXT NOT NULL,
            'Rating' TEXT NOT NULL,
            'Runtime' TEXT NOT NULL,
            'Plot' TEXT NOT NULL,
            'Director' TEXT NOT NULL,
            'LeadActor' TEXT NOT NULL,
            'OscarNoms' INTEGER,
            'OscarsWon' INTEGER
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
def insert_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for movie in final_movie_dict.keys():
        CriticImdbScore=final_movie_dict[movie]['Metascore']
        UserImdbScore=final_movie_dict[movie]['UserReview']
        if final_movie_dict[movie]['BoxOffice']!='Not released':
            BoxOfficeMoney=float(final_movie_dict[movie]['BoxOffice'][1:-1])
        else:
            BoxOfficeMoney='Not released'
        insertion=(None, CriticImdbScore, UserImdbScore, BoxOfficeMoney)
        statement='''
        INSERT INTO 'Movie_Reviews'
        Values (?, ?, ?, ?)
        '''
        cur.execute(statement, insertion)
    conn.commit()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for movie in final_movie_dict.keys():
        MovieName=movie
        ReleaseYear=final_movie_dict[movie]['ReleaseYear']
        Genre=final_movie_dict[movie]['Genre']
        Rating=final_movie_dict[movie]['Rating']
        Runtime=final_movie_dict[movie]['Runtime']
        Plot=final_movie_dict[movie]['Plot']
        Director=final_movie_dict[movie]['Director']
        LeadActor=final_movie_dict[movie]['Star']
        OscarNoms=final_movie_dict[movie]['OscarNominations']
        OscarsWon=final_movie_dict[movie]['OscarsWon']
        insertion=(None, MovieName, ReleaseYear, Genre, Rating, Runtime, Plot, Director, LeadActor, OscarNoms, OscarsWon)
        statement='''
        INSERT INTO 'Movie_Information'
        Values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(statement, insertion)
    conn.commit()
    conn.close()
#---------------------------------------------------------------------------------------------
help_commands='''
--------------------------------5-COMMANDS-AVAILABLE------------------------------------
         1. info all info <movie name>
                 -returns all the data for specified movie
                 -<movie name> must be capitalized
         2. info <data type> <movie name>
                -returns specific data type for specified movie
                -<data type> and <movie name> must be capitalized
         3. graph reviews <release date>
                 -displays a double bar graph of the top 20 critic rated movies
                 -bar graph will display critic and user rating in specified year
         4. graph boxoffice <release year>
                -displays a line graph of the top 20 grossing movies
                -line graph will display the amount of money each movie made
         5. graph genre <release year>
                -displays a bar graph of how many movies in each genre were made
                in specified release year
         6. graph oscars
                -double bar graph displaying oscar nominations and oscars won for
                each movie in the database
         4. exit
                 -exits the program
         5. help
                 -lists available commands (these instructions)
----------------------------------------------------------------------------------------
'''
def interactive_part():
    while True:
        user_input = input("Enter command: ")
        command = user_input.split()
        if command[0]=='info':
            if command[1]=='all' and command[2]=='info':
                try:
                    movie=''
                    for x in command[3:]:
                        movie+=x
                        movie+=' '
                    movie=movie.strip()
                    print(movie)
                    print('Release Year: ', final_movie_dict[movie]['ReleaseYear'])
                    print('Genre: ', final_movie_dict[movie]['Genre'])
                    print('Rating: ', final_movie_dict[movie]['Rating'])
                    print('Runtime: ', final_movie_dict[movie]['Runtime'])
                    print('Plot: ', final_movie_dict[movie]['Plot'])
                    print('Box Office: ', final_movie_dict[movie]['BoxOffice'])
                    print('User Review: ', final_movie_dict[movie]['UserReview'])
                    print('Critic Review: ', final_movie_dict[movie]['Metascore'])
                    print('Director: ', final_movie_dict[movie]['Director'])
                    print('Lead Actor: ', final_movie_dict[movie]['Star'])
                    print('Oscar Nominations: ', final_movie_dict[movie]['OscarNominations'])
                    print('Oscar Awards: ', final_movie_dict[movie]['OscarsWon'])
                except:
                    print('Invalid Entry! Make sure the movie title is spelled correctly.')
            else:
                try:
                    movie=''
                    for x in command[2:]:
                        movie+=x
                        movie+=' '
                    movie=movie.strip()
                    info_item=command[1]
                    print(info_item+' for '+movie+': ', final_movie_dict[movie][info_item])
                except:
                    print('Invalid Entry! Make sure data type is capitalized and the movie title is spelled correctly. If data type is two words please enter as one word with the first letter in both being capitalized.')
        elif command[0]=='graph':
            conn=sqlite3.connect(DBNAME)
            cur=conn.cursor()
            if command[1]=='reviews': #double bar graph user vs. critic score of top 20 movies in specified year
                try:
                    print("Creating double bar graph...")
                    statement='SELECT MovieName, UserImdbScore, CriticImdbScore '
                    statement+='FROM Movie_Reviews '
                    statement+='JOIN Movie_Information ON Movie_Information.Id=Movie_Reviews.Id '
                    statement+='WHERE ReleaseYear={} '.format(command[2])
                    statement+='ORDER BY UserImdbScore DESC LIMIT 20'
                    cur.execute(statement)
                    movie_list=[]
                    user_list=[]
                    critic_list=[]
                    for row in cur:
                        movie_name=row[0]
                        movie_list.append(movie_name)
                        user_review=float(row[1])
                        user_list.append(user_review)
                        critic_review=float(row[2])
                        critic_list.append(critic_review)
                    trace1 = go.Bar(
                        x=movie_list,
                        y=user_list,
                        name='User Reviews'
                    )
                    trace2 = go.Bar(
                        x=movie_list,
                        y=critic_list,
                        name='Critic Reviews'
                    )
                    data = [trace1, trace2]
                    layout = go.Layout(
                        barmode='group'
                    )
                    fig = go.Figure(data=data, layout=layout)
                    py.plot(fig, filename='User vs. Critic Score for Top 20 User Rated Movies in {}').format(command[2])
                except:
                    print('Invalid command! Make sure you enter a valid year. Enter "help" for list of commands.')
            elif command[1]=='boxoffice': #scatter plot of box office money for top 20 movies in specified year
                try:
                    print('Creating scatter plot...')
                    statement='SELECT MovieName, BoxOfficeMoney '
                    statement+='FROM Movie_Reviews '
                    statement+='JOIN Movie_Information '
                    statement+='ON Movie_Reviews.Id=Movie_Information.Id '
                    statement+='WHERE BoxOfficeMoney!="Not released" AND ReleaseYear={} '.format(command[2])
                    statement+='ORDER BY BoxOfficeMoney DESC LIMIT 20 '
                    cur.execute(statement)
                    movie_list=[]
                    box_office=[]
                    for row in cur:
                        movie_list.append(row[0])
                        box_office.append(float(row[1]))
                    trace2 = {"x": movie_list,
                              "y": box_office,
                              "marker": {"color": "blue", "size": 12},
                              "mode": "markers",
                              "type": "scatter",
                              }
                    data=[trace2]
                    layout={"title": "Top 20 Grossing Movies in {}".format(command[2]),
                              "xaxis": {"title": "Movie Name", },
                              "yaxis": {"title": "Box Office Money (in millions of dollars)"}}
                    fig=go.Figure(data=data, layout=layout)
                    py.plot(fig, filenmae='Top 20 Grossing Movies')
                except:
                    print('Invalid Command. Make sure you enter a valid year. Enter "help" for list of commands.')
            elif command[1]=='genre': #bar graph of how many movies in each genre was made in the specified calender year
                try:
                    print('Creating bar graph...')
                    statement='SELECT MovieName, Genre, ReleaseYear '
                    statement+='FROM Movie_Information '
                    statement+='WHERE ReleaseYear={}'.format(command[2])
                    cur.execute(statement)
                    movie_list=[]
                    genre_list=[]
                    for row in cur:
                        movie_list.append(row[0])
                        genre_list.append(row[1])
                    family_counter=0
                    action_counter=0
                    comedy_counter=0
                    thriller_counter=0
                    animation_counter=0
                    horror_counter=0
                    biography_counter=0
                    mystery_counter=0
                    crime_counter=0
                    fantasy_counter=0
                    sci_fi_counter=0
                    for x in genre_list:
                        if 'Family' in x:
                            family_counter+=1
                        if 'Action' in x:
                            action_counter+=1
                        if 'Comedy' in x:
                            comedy_counter+=1
                        if 'Thriller' in x:
                            thriller_counter+=1
                        if 'Animation' in x:
                            animation_counter+=1
                        if 'Horror' in x:
                            horror_counter+=1
                        if 'Biography' in x:
                            biography_counter+=1
                        if 'Mystery' in x:
                            mystery_counter+=1
                        if 'Crime' in x:
                            crime_counter+=1
                        if 'Fantasy' in x:
                            fantasy_counter+=1
                        if 'Sci-Fi' in x:
                            sci_fi_counter+=1
                    data = [go.Bar(
                            x=['Family', 'Action', 'Comedy', 'Thriller', 'Animation', 'Horror', 'Biography', 'Mystery', 'Crime', 'Fantasy', 'Sci-Fi'],
                            y=[family_counter, action_counter, comedy_counter, thriller_counter, animation_counter, horror_counter, biography_counter, mystery_counter, crime_counter, fantasy_counter, sci_fi_counter]
                            )]
                    py.plot(data, filename='basic-bar')
                except:
                    print('Invalid command. Make sure you enter a valid year. Enter "help" for list of commands.')
            elif command[1]=='oscars':#double bar graph showing the oscar nominatoins and oscars won
                try:
                    print("Creating double bar graph...")
                    statement='SELECT MovieName, OscarNoms, OscarsWon '
                    statement+='FROM Movie_Information '
                    statement+='WHERE OscarNoms!="None" AND OscarsWon!="None" '
                    statement+='ORDER BY OscarNoms DESC LIMIT 20'
                    cur.execute(statement)
                    movie_list=[]
                    oscarnom_list=[]
                    oscarswon_list=[]
                    for row in cur:
                        movie_list.append(row[0])
                        oscarnom_list.append(row[1])
                        oscarswon_list.append(row[2])
                    trace1 = go.Bar(
                        x=movie_list,
                        y=oscarnom_list,
                        name='Oscar Nominations'
                    )
                    trace2 = go.Bar(
                        x=movie_list,
                        y=oscarswon_list,
                        name='Oscars Won'
                    )
                    data = [trace1, trace2]
                    layout = go.Layout(
                        barmode='group'
                    )
                    fig = go.Figure(data=data, layout=layout)
                    py.plot(fig, filename='Oscar Nominations and Oscar Wins for Top 20 Oscar Nominated Movies')
                except:
                    print("Invalid command. Enter 'help' for list of commands.")
            conn.commit()
            conn.close()
        elif command[0]=='exit':
            print("GOODBYE! COME BACK FOR MORE MOVIES!")
            break
        elif command[0]=='help':
            print(help_commands)
            continue
        else:
            print("Please enter a valid command. Enter 'help' for list of commands.")

if __name__ == "__main__":
    interactive_part()
