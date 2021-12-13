# import libriaries
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity

from math import*
 
def manhattan_distance(x,y):
 
    return sum(abs(a-b) for a,b in zip(x,y))
 
def euclidean_distance(x,y):
 
    return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

# import the data and create revelent dataframes
def load():
    # url = 'https://www.nestpick.com/work-from-anywhere-index/'

    df = pd.read_csv('city_ranking.csv',header=0)
    
    df.fillna(df.mean)

    data = df.set_index('City').iloc[1,1:-1]
    scores = df.set_index('City').iloc[:,1:-1].round()
    location = []
    for index, city, country in df[["City", "Country"]].sort_values("Country").itertuples():
        new = f'{city}, {country}'
        location.append(new)
    return df, data,scores, location

#Calculate the cosine-similarity
def find_similarity(column, user, number,scores, city, numberOfCities): # city == staden man kommer ifrån, number = antalet prefenser, user = värden från sliders
    if city == 'Others':
        new_df = scores[column]
    else:
        locate = city.split(',') #get only the city
        new_df = scores[scores.index !=  locate[0]][column] #don´t get the city youre from
    value = []
    for index,city in enumerate(new_df.index):
        city_old = new_df.loc[city].values.reshape(-1,number) #loc = access a group of rows and columns by label. We get al the cities values depending on our choosen features.
        user = user.reshape(-1, number)
        score = cosine_similarity(city_old, user)
        #score = euclidean_distance(city_old[0], user[0])
        value.append(score) # sparar värdet i value
        #value.append(score.all()) # sparar värdet i value
        #print(city_old, score, sep='__________\n' )
       

    similarity = pd.Series(value, index=new_df.index)
    city_similar = similarity.sort_values(ascending=False).astype(float).iloc[0:numberOfCities] #Instead of idxmax use 5 top values for multiple cities?
    print("City_Similarity : ", city_similar)
    print(value[0], "+++++++++")

    # message = f'Based on your aggregate preferences and ratings, {city_similar} is the top recommended city to move/travel to.'
    return city_similar

# Get more info about the recommended city
def final_answer(df,word, data):
    title = f'About {word}'
    country = df.loc[df['City'] == word, 'Country'].iloc[0]

    return title, country 

#The app controller
def main():
    print("-----------START----------")
    st.title('City Recommender')
    df, data,scores, location = load()
    location.append('Others')
    numbers = ([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50])
    city = st.selectbox("Location of Residence", location)
    numberOfCities= st.selectbox("Choose how many cities to recommend", numbers)
    preference = st.multiselect("Choose the 5 features that matters to you the most in a city",scores.columns)
    if st.checkbox("Rate the features"):
         if len(preference) == 5 :
            level1 = st.slider(preference[0], 1,10)
            level2 = st.slider(preference[1], 1,10)
            level3 = st.slider(preference[2], 1,10)
            level4 = st.slider(preference[3], 1,10)
            level5 = st.slider(preference[4], 1,10)
            if st.button("Recommend", key="hi"):
                user = np.array([level1,level2,level3,level4,level5]) 

                column = preference # hämtar kolumn siffror för varje preferens som användaren fyllt i
                number = len(preference)
                city_similar = find_similarity(column, user, number,scores,city, numberOfCities)

                city_similar.to_csv('newTextFile.csv')
                df_cities = pd.read_csv('newTextFile.csv', usecols=['City', '0'])
                df_cities["City"].to_csv('nameOfCities.csv')
                df_cities["0"].to_csv('scoresOfCities.csv')
                
                #for index, val in enumerate(df): # ändra 1an till index
                    
                
                    
                with st.spinner("Analysing..."):
                    time.sleep(5)
                st.text(f'\n\n\n')
                st.markdown('--------------------------------------------**Recommendation**--------------------------------------------')
                st.text(f'\n\n\n\n\n\n')
                
                st.markdown(f'Based on your aggregate preferences and ratings, ')
                for index, val in enumerate(df_cities["City"]): # ändra 1an till index
                    st.markdown(f'{index+1}. **{df_cities["City"][index]}**')
                st.markdown(f'are the top {numberOfCities} recommended cities to move/travel to.')
                for index, val in enumerate(df_cities["City"]): # ändra 1an till index
                    (title, country) = final_answer(df, df_cities["City"][index], data)
                    st.text(f'\n\n\n\n\n\n')
                    st.markdown(f'----------------------------------------------**{title}**---------------------------------------------')
                    st.write(f'{df_cities["City"][index]} is a city in {country}.')
                st.markdown(f'For more info on city rank scores, check [here](https://www.nestpick.com/work-from-anywhere-index/)')


         elif len(preference) > 5:
              st.warning("choose only 5 features")
         else:
             st.error("You are to choose at least 5 feature from the bove options")

if __name__ == "__main__":
    main()
