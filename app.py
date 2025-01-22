import streamlit as st
import sqlite3
import os
import pandas as pd

def db_tree_view(db_name):
    result = [f"{db_name}/"]
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table, in cursor.fetchall():
        result.append(f"├── {table}")
        cursor.execute(f"PRAGMA table_info({table});")
        for column in cursor.fetchall():
            result.append(f"│   ├── {column[1]} ({column[2]})")
    conn.close()
    return "\n".join(result)

st.set_page_config(page_title="SQL Queries",page_icon='')
tailwind_cdn = """
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.23/dist/full.min.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>
"""
st.markdown(tailwind_cdn, unsafe_allow_html=True)
hide_streamlit_style = "<style>#MainMenu, footer, header {visibility: hidden;}</style>"
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title("Database Terminal")

db_files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.db')]
st.sidebar.write(f"## {len(db_files)} sqlite databases found \n ")
db = st.sidebar.selectbox("Select database", db_files)
conn = sqlite3.connect(db) # Connect to a SQLite database (or create it if it doesn't exist)
cursor = conn.cursor()
st.sidebar.write("``` \n " + db_tree_view(db)+ " \n ```")

with st.expander("SQL Cheat Sheet"):
   st.markdown("""
    ### Basic Queries
    **Create a Table**
    ```sql
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    );
    ```

    **Insert Data**
    ```sql
    INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
    ```

    **Select All Records**
    ```sql
    SELECT * FROM users;
    ```

    **Filter Data**
    ```sql
    SELECT * FROM users WHERE name = 'Alice';
    ```
    """)

if db:
  query = st.text_area("Enter your SQL lite query here:", height=200)

  if st.button("Run"):
    try:
      cursor.execute(query)
      conn.commit()
      if any(query.upper().startswith(keyword) for keyword in ["SELECT", "SHOW", "DESCRIBE", "EXPLAIN"]):
        response = cursor.fetchall()
        df = pd.DataFrame(response)
        df.columns = [desc[0] for desc in cursor.description]
        st.dataframe(df,hide_index=True,use_container_width=True) 
    except Exception as e:
      st.error(f"Error executing query: {e}")
      conn.rollback()  # Rollback the transaction to reset the state
      st.error(f"Transaction rolled back.")
      st.info("Please try again")


#cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
#cursor.execute('''INSERT INTO users (name, age) VALUES (?, ?)''', ('Alice', 30))
#conn.commit()

## Query data
#cursor.execute('''SELECT * FROM users''')
#rows = cursor.fetchall()
#for row in rows:
#    print(row)

# Close the connection
#conn.close()