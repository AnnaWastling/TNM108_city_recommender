# import libriaries
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity

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
def find_similarity(column, user, number,scores, city): # city == staden man kommer ifrån, number = antalet prefenser, user = värden från sliders
    if city == 'Others':
        new_df = scores[column]
    else:
        locate = city.split(',') #get only the city
        new_df = scores[scores.index !=  locate[0]][column] #don´t get the city youre from
    value = []
    for index,city in enumerate(new_df.index):
        city_old = new_df.loc[city].values.reshape(-1,number) #loc = access a group of rows and columns by label
        user = user.reshape(-1, number)
        score = cosine_similarity(city_old, user)
        value.append(score) # sparar värdet i value
        # ÄNDRA HÄR FÖR ATT FÅ FLERA STÄDER
    similarity = pd.Series(value, index=new_df.index)
    city_similar = similarity.sort_values(ascending=False).astype(float).iloc[1:5] #Instead of idxmax use 5 top values for multiple cities?
    
    # message = f'Based on your aggregate preferences and ratings, {city_similar} is the top recommended city to move/travel to.'
    return city_similar

# Get more info about the recommended city
def final_answer(df,word, data):
    title = f'About {word}'
    country = df.loc[df['City'] == word, 'Country'].iloc[0]

    return title, country 

#The app controller
def main():
    st.title('City Recommender')
    df, data,scores, location = load()
    location.append('Others')
    city = st.selectbox("Location of Residence", location)
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
                city_similar = find_similarity(column, user, number,scores,city)

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
                    st.markdown(f'{index+1}. **{df_cities["City"][index]},**')
                st.markdown(f'are the top 4 recommended cities to move/travel to.')
                for index, val in enumerate(df_cities["City"]): # ändra 1an till index
                    (title, country) = final_answer(df, df_cities["City"][index], data)
                    st.text(f'\n\n\n\n\n\n')
                    st.markdown(f'----------------------------------------------**{title}**---------------------------------------------')
                    st.write(f'{df_cities["City"][index]} is a city in {country}.')
                   
                    #getCity = df[["City"]].loc[city]
                    #getCity.to_csv("Test")
                    #breakdown = pd.DataFrame(getCity, columns = ['Category','Score'])
                    #breakdown['Score'] = breakdown['Score'].round(1)
                    #st.table(breakdown.style.format({'Score':'{:17,.1f}'}).set_properties(subset=['Score'], **{'width': '250px'}))
                st.markdown(f'For more info on city rank scores, check [here](https://www.nestpick.com/work-from-anywhere-index/)')


         elif len(preference) > 5:
              st.warning("choose only 5 features")
         else:
             st.error("You are to choose at least 5 feature from the bove options")

if __name__ == "__main__":
    main()
