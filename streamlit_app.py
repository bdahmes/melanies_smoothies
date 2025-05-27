# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)
name_on_order = st.text_input('Name on Smoothie')
st.write(f'The name on the smoothie will be: {name_on_order}')

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'),col('search_on'))
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f'{fruit_chosen} Nutrition Information:')
        smoothiefroot_response = requests.get(f'https://my.smoothiefroot.com/api/fruit/watermelon')
        st.text(smoothiefroot_response.json())
        # smoothiefroot_response = requests.get(f'https://my.smoothiefroot.com/api/fruit/{search_on}')
        sf_df = st.dataframe(smoothiefroot_response.json(),use_container_width=True)
        
        my_insert_stmt = f""" insert into smoothies.public.orders(ingredients,name_on_order)
                values ('{ingredients_string}','{name_on_order}')"""
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")


