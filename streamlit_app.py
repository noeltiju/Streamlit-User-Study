import gspread, pandas as pd, streamlit as st, toml

spreadsheet_id = "1gCvF2PfMQpp1cVsbSpfzTG8ShN5GAktQ2kY8iLUb7mI"
scopes = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

service_account_info = st.secrets["gcp_service_account"]

gc = gspread.service_account_from_dict(service_account_info, scopes=scopes)
sh = gc.open_by_key(spreadsheet_id)
worksheet = sh.worksheet("User-Ratings")
data = worksheet.get_all_values()
user_ratings_attractions = pd.DataFrame(data[1:], columns = data[0])

def user_registration():
    st.markdown("<h3 style='text-align: center;'>Adding User Ratings</h3>", unsafe_allow_html=True)
    worksheet_mails = sh.worksheet("Contact_details")
    contact_data = worksheet_mails.get_all_values()
    mail_data = pd.DataFrame(contact_data[1:], columns = contact_data[0])
    state_ = st.selectbox('Select State', user_ratings_attractions['State'].unique())
    new_user = st.text_input('Enter your name')
    email_id = st.text_input('Enter your email id')
    if new_user != "" and email_id != "":
        if new_user not in user_ratings_attractions.columns:
            user_ratings_attractions[new_user] = 0
            new_user_info = pd.DataFrame([[new_user, email_id]], columns=mail_data.columns)
            updated_user_info_df = pd.concat([mail_data, new_user_info], ignore_index=True)
            worksheet_mails.clear()
            worksheet_mails.update([updated_user_info_df.columns.values.tolist()] + updated_user_info_df.values.tolist())

        available_attractions = user_ratings_attractions[user_ratings_attractions['State'] == state_]['Name'].tolist()
        with st.form(key='ratings_form'):
            st.write('Rate the attractions you have visited:')
            for attraction in available_attractions:
                existing_rating = user_ratings_attractions.loc[user_ratings_attractions['Name'] == attraction, new_user].values[0]

                rating = st.slider(f'{attraction}', min_value=0, max_value=5, value=int(existing_rating), step=1, key=f'rating_{attraction}')
                if rating != existing_rating:
                    user_ratings_attractions.loc[user_ratings_attractions['Name'] == attraction, new_user] = rating
            
            submit_button = st.form_submit_button('Submit Ratings')
        if submit_button:
            st.success('Ratings submitted successfully!')
            worksheet.clear()
            worksheet.update([user_ratings_attractions.columns.values.tolist()] + user_ratings_attractions.values.tolist())
            st.write("Data updated successfully!")

def user_recommendations():
    st.markdown("<h3 style='text-align: center;'>Tourist Attraction Recommendation System</h3>", unsafe_allow_html=True)
    worksheet_ratings = sh.worksheet("Predicted-User-Ratings")
    worksheet_attractions = sh.worksheet("Attractions")
    ratings_data = worksheet_ratings.get_all_values()
    ratings_data = pd.DataFrame(ratings_data[1:], columns = ratings_data[0])

    attractions_data = worksheet_attractions.get_all_values()
    attractions_data = pd.DataFrame(attractions_data[1:], columns = attractions_data[0])

    user = st.selectbox('Select User', list(ratings_data.columns[1:]))
    type = st.selectbox('State/Country', ['State','Country'])
    number_of_attractions = st.slider('Number of attractions to recommend', min_value=1, max_value=10, value=5, step=1)
    if user and type == 'State':
        state = st.selectbox('Select State', attractions_data['State'].unique())
        result = recommendations_state(attractions_data, ratings_data, number_of_attractions, state, user)

        for i in range(len(result)):
            st.write(f"Name: {result[i]['Name']}")
            st.write(f"City: {result[i]['City']}")
            st.write(f"Opening Hours: {result[i]['Opening Hours']}")
            st.write(f"Description: {result[i]['Description']}")
            st.write('--------------------------------')
    elif user and type == 'Country':
        country = st.selectbox('Select Country', user_ratings_attractions['Country'].unique())
        result = recommendations_country(attractions_data, ratings_data, number_of_attractions, country, user)

        for i in range(len(result)):
            st.write(f"Name: {result[i]['Name']}")
            st.write(f"State: {result[i]['State']}")
            st.write(f"City: {result[i]['City']}")
            st.write(f"Opening Hours: {result[i]['Opening Hours']}")
            st.write(f"Description: {result[i]['Description']}")
            st.write('--------------------------------')



def recommendations_state(attractions_data, user_ratings_data, number_of_attractions, state, user):
    attraction_names = []
    attractions_description = {}
    for i in range(len(attractions_data)):
        if (attractions_data['State'][i] == state):
            attraction_names.append(attractions_data['Name'][i])
            attractions_description[attractions_data['Name'][i]] = [attractions_data['City'][i], attractions_data['Opening Hours'][i], attractions_data['Description'][i]]

    attractions  = {}

    for i in range(len(user_ratings_data)):
        if user_ratings_data['Name'][i] in attraction_names:
            attractions[user_ratings_data['Name'][i]] = user_ratings_data[user][i]


    attractions_sorted = dict(sorted(attractions.items(), key=lambda item: item[1], reverse=True))
    result = []
    count = 0
    for name in attractions_sorted.keys():
        if count == number_of_attractions:
            break
        count+=1

        result.append({'Name': name, 'City': attractions_description[name][0], 'Opening Hours': attractions_description[name][1], 'Description': attractions_description[name][2]})
    return result

def recommendations_country(attractions_data, user_ratings_data, number_of_attractions, country, user):
    attraction_names = []
    attractions_description = {}
    for i in range(len(attractions_data)):
        if (attractions_data['Country'][i] == country):
            attraction_names.append(attractions_data['Name'][i])
            attractions_description[attractions_data['Name'][i]] = [attractions_data['City'][i], attractions_data['Opening Hours'][i], attractions_data['Description'][i], attractions_data['State'][i]]

    attractions  = {}

    for i in range(len(user_ratings_data)):
        if user_ratings_data['Name'][i] in attraction_names:
            attractions[user_ratings_data['Name'][i]] = user_ratings_data[user][i]


    attractions_sorted = dict(sorted(attractions.items(), key=lambda item: item[1], reverse=True))
    result = []
    count = 0
    for name in attractions_sorted.keys():
        if count == number_of_attractions:
            break
        count+=1

        result.append({'Name': name, 'City': attractions_description[name][0], 'Opening Hours': attractions_description[name][1], 'Description': attractions_description[name][2], 'State': attractions_description[name][3]})

    return result


def intro_page():
    st.markdown("<h1 style='text-align: center;'>Roamify</h1>", unsafe_allow_html=True)
    page = st.sidebar.radio('Go to', ['Home','Add User Ratings'])
    if page == 'Add User Ratings':
        user_registration()
    elif page == 'Home':
        user_recommendations()
if __name__ == '__main__':
   intro_page()
    