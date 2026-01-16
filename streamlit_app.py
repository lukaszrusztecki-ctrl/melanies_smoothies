# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# =========================
# APP HEADER
# =========================
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("**Choose the fruits you want in your custom Smoothie!**")

# =========================
# USER INPUT
# =========================
name_on_order = st.text_input(
    'Name on Smoothie:',
    key='name_on_order_input'
)

st.write('The Name on your Smoothie will be:', name_on_order)

# =========================
# SNOWFLAKE CONNECTION
# =========================
cnx = st.connection("snowflake")
session = cnx.session()

# =========================
# LOAD FRUIT OPTIONS
# =========================
fruit_df = session.table(
    "smoothies.public.fruit_options"
).select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert to Pandas for SEARCH_ON lookup
pd_df = fruit_df.to_pandas()

# =========================
# INGREDIENT SELECTION
# =========================
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5,
    key='ingredients_multiselect'
)

# =========================
# DISPLAY NUTRITION DATA
# =========================
ingredients_string = ''

if ingredients_list:
    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            smoothiefroot_response.json(),
            use_container_width=True
        )

# =========================
# SUBMIT ORDER (STABLE UI)
# =========================
if ingredients_list and name_on_order:
    submit_order = st.button(
        'Submit Order',
        key='submit_order_button'
    )

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


