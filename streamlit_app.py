# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write(
    """**Choose the fruits you want in your custom Smoothie!**"""
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The Name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DF → Pandas DF (needed for .loc)
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,   # GUI still shows FRUIT_NAME
    max_selections=5
)

# =========================
# DISPLAY NUTRITION DATA
# =========================
ingredients_string = ''  # ✅ FIX: moved OUTSIDE the loop

if ingredients_list:
    for fruit_chosen in ingredients_list:

        # ✅ FIX: build string safely
        ingredients_string += fruit_chosen + ' '

        # ✅ FIX: lookup SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

# =========================
# SUBMIT ORDER (MUST BE OUTSIDE LOOP)
# =========================
if ingredients_list and name_on_order:   # ✅ FIX: stable condition
    submit_order = st.button('Submit Order')

    if submit_order:
        session.sql(
            """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (?, ?)
            """,
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(
            f'Your Smoothie is ordered {name_on_order}!',
            icon="✅"
        )
# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write(
    """**Choose the fruits you want in your custom Smoothie!**"""
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The Name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
        st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True
        )

