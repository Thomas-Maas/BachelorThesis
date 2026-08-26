import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"]
)


cur = conn.cursor()

def execute_query(query: str):
    """
    Perform a SQL query and print results like:
    'Witness: Betty, Sentence: value'
    """
    cur.execute(query)

def execute_query_print(query: str):
    """
    Perform a SQL query and print results like:
    'Witness: Betty, _sentence: value'
    """
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]

    for row in rows:
        parts = []
        for i, (col, val) in enumerate(zip(colnames, row)):
            label = col.capitalize() if i == 0 else col
            parts.append(f"{label}: {val}")
        print(", ".join(parts))

def analyze_query(query: str):
    """
    Analyze a SQL query and return the execution plan.
    """
    cur.execute(f"EXPLAIN ANALYZE {query}")
    rows = cur.fetchall()
    for row in rows:
        print(row)

def execute_query_print_and_analyze(query: str):
    """
    Perform a SQL query and analyze it.
    """
    print(f"Query: {query}")
    execute_query_print(query)
    analyze_query(query)

def execute_query_and_analyze(query: str):
    """
    Perform a SQL query and analyze it.
    """
    print(f"Query: {query}")
    execute_query(query)
    analyze_query(query)

# Gets all dict entries
get_dict_values = "SELECT print(dict) FROM _dict;"

# Get all entries from the 'drives' table
get_drives_table = "SELECT * FROM drives;"

# Get all entries from the 'saw' table
get_saw_table = "SELECT * FROM saw;"


#  Gets witness name and color of car they saw with the sentence
#query_agg_or = "SELECT witness, color, agg_or(_sentence) AS _sentence FROM saw WHERE witness = 'diane' GROUP BY witness, color"

#join_query_test = "SELECT saw.witness, drives.person, saw.color, agg_or(drives._sentence & saw._sentence) AS _sentence FROM drives, saw WHERE saw.color = drives.color GROUP BY saw.color, saw.witness, drives.person"
#join_query_test_prob = "SELECT saw.witness, drives.person, saw.color, prob(d.dict, agg_or(drives._sentence & saw._sentence)), agg_or(drives._sentence & saw._sentence) AS _sentence FROM drives, saw, _dict d WHERE saw.color = drives.color AND d.name='mydict' GROUP BY saw.color, saw.witness, drives.person"
#execute_query_print(get_dict_values)



#Add new person to the drives table
#execute_query("DROP TABLE IF EXISTS trustworthy")


#execute_query("UPDATE _dict SET dict=add(dict,'d4=1:0.8;d4=2:0.2;') WHERE name='mydict';")
#execute_query("UPDATE _dict SET dict=add(dict,'t1=1:0.2;t1=2:0.8; t3=1:0.8;t3=2:0.2; t4=1:0.05;t4=2:0.95') WHERE name='mydict';")
#execute_query("CREATE TABLE trustworthy (id integer, witness text, _sentence Bdd);")
#execute_query("INSERT INTO trustworthy VALUES (1, 'amy', Bdd('t1=1')), (2, 'betty', Bdd('1')), (3, 'cathy', Bdd('t3=1')), (4, 'diane', Bdd('t4=1'));")

#execute_query("DELETE FROM drives WHERE person = 'thomas';")
#execute_query("INSERT INTO drives VALUES (4,'thomas','red','toyota',Bdd('d4=1')), (4,'thomas','blue','toyota',Bdd('d4=2'));")




ex_1 = "SELECT witness, _sentence FROM saw WHERE car = 'toyota'"
ex_2 = "SELECT s.witness, d.person AS suspect, (s._sentence & d._sentence & t._sentence) AS _sentence FROM saw s, drives d, trustworthy t WHERE s.color = d.color AND s.car = d.car AND t.witness = s.witness"
execute_query_print(ex_1)
execute_query_print(ex_2)
execute_query("DROP VIEW IF EXISTS suspects_witnesses CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW suspects_witnesses AS {ex_2}")
execute_query_print("SELECT s.*, round(prob(d.dict, s._sentence)::numeric,4) AS prob FROM suspects_witnesses s, _dict d WHERE d.name = 'mydict'")
execute_query("DROP VIEW IF EXISTS suspects;")
ex_4 = "CREATE OR REPLACE VIEW suspects AS SELECT s.suspect, agg_or(s._sentence) AS _sentence FROM suspects_witnesses s GROUP BY s.suspect"
execute_query(ex_4)
execute_query_print("SELECT * FROM suspects")
execute_query_print("SELECT s.*, round(prob(d.dict, s._sentence)::numeric,4) AS prob FROM suspects s, _dict d WHERE d.name = 'mydict' ORDER BY prob DESC")






# 6. Close cursor and connection
cur.close()
conn.close()

