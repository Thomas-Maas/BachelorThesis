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

#execute_query_print(prob)
 # We will now construct a dummy dictionary to hold all unique variables and their probabilities using the dual relation variable table. If the variables values do not add up to 1, create a dummy variable with the remaining probability. Dummy value is max value + 1
#TODO Make it so that a table where all values of a var dont add up to 1, a dummy variable is created with the remaining probability. Dummy value is max value + 1 and probability of 1- sum(prob)
#Utility function that creates a Dubio dict from a table of (varval, prob) tuples
    #create_dict_from_dual = f"""
    #SELECT 
    #print(dictionary(string_agg(varval || ':' || prob::text, '; ') || ';')) AS final_dictionaryaaa
    #FROM ({join_probability_on_duo_vars}) AS final;
    #"""

#Utility function that creates a Dubio dict from a table of (var, val, prob) tuples
   # create_dict_from_triple = f"""
    #SELECT 
    #print(dictionary(string_agg(var || '=' || val || ':' || prob::text, '; ') || ';')) AS final_dictionaryaaa
    #FROM ({join_probability_on_triple_vars}) AS final;
    #"""





def create_dual_relation_prob_query(table_getting_query: str):
    """
    Create a query to create a dual relation probability result.
    """
    # 1. Get all sentences from the relevant table
    get_sentence_string = f"SELECT tostring(_sentence) as stringsent FROM ({table_getting_query}) AS t"

    # 2.1. Get all variables that occur in a sentence, give the sentence an ID and match appropriate variables to this ID
    get_dual_sentence_vars = f"SELECT ranked_sentences.id, varval FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM ({table_getting_query}) AS t) AS ranked_sentences, LATERAL regexp_split_to_table(ranked_sentences.stringsent, '[()&!|]+') AS varval WHERE varval <> '' AND varval <> '1' UNION SELECT ranked.id, '1' AS varval FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM ({table_getting_query}) AS t WHERE tostring(_sentence) = '1') AS ranked"



    


    #Remove parentheses and ampersands from the sentence string, take distinct values, only non 1 or nonempty values
    extract_relevant_duo_vars = f"""SELECT DISTINCT varval 
                            FROM ({get_sentence_string}) as ss, 
                            LATERAL regexp_split_to_table(ss.stringsent, '[()&!|]+') AS varval 
                            WHERE varval <> '1' AND varval <> '' ORDER BY varval"""
    # Join the variables' probabilities on the UNIQUE table of variables  (varval, prob) e.g. (a1=2, 0.5)
    join_probability_on_duo_vars = f"""SELECT rdv.varval, dr.prob FROM ({extract_relevant_duo_vars}) as rdv JOIN dualrelation dr ON rdv.varval = dr.varval"""
    #create view showing the unique variables

   


    #For the entire table find replace variables with their probability value found in UNIQUE relevant probility table (named dualrelationvarsprob as a view above)
    grouped_sentences_dual_prob_join = f"SELECT dsv.id, CASE WHEN dsv.varval = '1' THEN 1.0 ELSE drvp.prob END AS prob FROM ({get_dual_sentence_vars}) AS dsv LEFT JOIN ({join_probability_on_duo_vars}) drvp ON dsv.varval = drvp.varval"

    

    #Now group by ID for both dual and triple relations, aggregate probability values by multiplying them
    grouped_dual_prob = f"SELECT idprobs.id, exp(sum(ln(idprobs.prob))) as prob FROM ({grouped_sentences_dual_prob_join}) as idprobs GROUP BY idprobs.id ORDER BY idprobs.id"
    
    #Re input sentence instead of ID, so that we can see the sentence and its probability. For dual relations:
    final_sentence_prob_dual = f"SELECT ranked_sentences.stringsent, gdp.prob FROM (SELECT DISTINCT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM ({table_getting_query}) AS t) AS ranked_sentences JOIN ({grouped_dual_prob}) AS gdp ON ranked_sentences.id = gdp.id ORDER BY ranked_sentences.id"
    
    return final_sentence_prob_dual


    

def create_triple_relation_prob_query(table_getting_query: str):
    """
    Create a query to create a triple relation probability result.
    """
    get_sentence_string = f"SELECT tostring(_sentence) as stringsent FROM ({table_getting_query}) AS t"
    # 2.2. Get all variables that occur in a sentence, give the sentence an ID and match appropriate variables to this ID, split on =, to make this a triple relation
    get_triple_sentence_vars = f"SELECT ranked_sentences.id, matches[1] AS var, matches[2]::int AS val FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM ({table_getting_query}) AS t) AS ranked_sentences, LATERAL regexp_split_to_table(ranked_sentences.stringsent, '[()&!|]+') AS val, LATERAL regexp_matches(val, '^([a-zA-Z0-9]+)=([0-9]+)$') AS matches WHERE val <> '' AND val <> '1' UNION SELECT ranked.id, '1' AS var, 1 AS val FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM ({table_getting_query}) AS t WHERE tostring(_sentence) = '1') AS ranked"
     #Remove parentheses and ampersands from the sentence string, take distinct values, only non 1 or nonempty values, split on =
    extract_relevalt_triple_vars = f"""SELECT DISTINCT matches[1] as var, matches[2]::int as val 
                                FROM ({get_sentence_string}) as ss, LATERAL regexp_split_to_table(ss.stringsent, '[()&!|]+') AS val,
                                LATERAL regexp_matches(val, '^([a-zA-Z0-9]+)=([0-9]+)$') AS matches 
                                WHERE val <> '' ORDER BY var, val"""
    # Join the variables' probabilities on the UNIQUE table of variables  (var, val, prob) e.g. (a1, 2, 0.5)
    join_probability_on_triple_vars = f"""SELECT rtv.var, rtv.val, tr.prob FROM ({extract_relevalt_triple_vars}) as rtv JOIN triplerelation tr ON rtv.var = tr.var AND rtv.val = tr.val"""
    #For the entire table find replace variables with their probability value found in UNIQUE relevant probility table (named triplerelationvarsprob as a view above)
    grouped_sentences_triple_prob_join = f"SELECT tsv.id, CASE WHEN tsv.var = '1' AND tsv.val = 1 THEN 1.0 ELSE trvp.prob END AS prob FROM ({get_triple_sentence_vars}) AS tsv LEFT JOIN ({join_probability_on_triple_vars}) trvp ON tsv.var = trvp.var AND tsv.val = trvp.val"
    #Now group by ID for both dual and triple relations, aggregate probability values by multiplying them
    grouped_triple_prob = f"SELECT idprobs.id, exp(sum(ln(idprobs.prob))) as prob FROM ({grouped_sentences_triple_prob_join}) as idprobs GROUP BY idprobs.id ORDER BY idprobs.id"
    #Re input sentence instead of ID, so that we can see the sentence and its probability. For triple relations:
    final_sentence_prob_triple = f"SELECT ranked_sentences.stringsent, gtp.prob FROM (SELECT DISTINCT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM ({table_getting_query}) AS t) AS ranked_sentences JOIN ({grouped_triple_prob}) AS gtp ON ranked_sentences.id = gtp.id ORDER BY ranked_sentences.id"
    
    return final_sentence_prob_triple

#Now create a view that shows the entire t_witness table with probability using base dubio, the probability using dual sentence, the probability using triple sentence


#execute_query_print(final_sentence_prob_dual)
#execute_query_print(final_sentence_prob_triple)
#execute_query_print("SELECT prob(d.dict, _sentence) FROM t_witnesses t, _dict d WHERE d.name = 'thomasdict'")
#execute_query_print(all_witness_probs)#


def analyze_dual_relation_prob(table_getting_query: str):
    """
    Analyze the dual relation probabilities from a table.
    """
    query = create_dual_relation_prob_query(table_getting_query)
    execute_query_and_analyze(query)

def analyze_triple_relation_prob(table_getting_query: str):
    """
    Analyze the triple relation probabilities from a table.
    """
    query = create_triple_relation_prob_query(table_getting_query)
    execute_query_and_analyze(query)

def print_prob_dual_from_table(table_getting_query: str):
    """
    Print the dual relation probabilities from a table.
    """
    query = create_dual_relation_prob_query(table_getting_query)
    execute_query_print(query)

def print_prob_triple_from_table(table_getting_query: str):
    """
    Print the triple relation probabilities from a table.
    """
    query = create_triple_relation_prob_query(table_getting_query)
    execute_query_print(query)

def create_all_probs_from_table(table_getting_query: str):
    """
    Print all entries and probabilities using all methods from a dynamic table query.
    """
    final_sentence_prob_dual = create_dual_relation_prob_query(table_getting_query)
    final_sentence_prob_triple = create_triple_relation_prob_query(table_getting_query)

    all_witness_probs = f"""
    SELECT 
      t.*, 
      CASE 
        WHEN tostring(t._sentence) = '1' THEN 1
        ELSE prob(d.dict, t._sentence)
      END AS base_prob,
      COALESCE(final_dual.prob, 1) AS dual_prob,
      COALESCE(final_triple.prob, 1) AS triple_prob
    FROM 
      ({table_getting_query}) AS t
      JOIN _dict d ON d.name = 'thomasdict'
      LEFT JOIN ({final_sentence_prob_dual}) AS final_dual 
        ON tostring(t._sentence) = final_dual.stringsent
      LEFT JOIN ({final_sentence_prob_triple}) AS final_triple 
        ON tostring(t._sentence) = final_triple.stringsent
    ORDER BY 
      tostring(t._sentence)
    """
    return all_witness_probs

def print_all_from_table(table_getting_query: str):
    """
    Print all entries and probabilities using all methods from a dynamic table query.
    """
    query = create_all_probs_from_table(table_getting_query)
    execute_query_print(query)

def create_all_probs_performance_view(table_getting_query: str):
    """
    Create a view that shows all probabilities from a table.
    """
    query = create_all_probs_from_table(table_getting_query)
    execute_query("DROP VIEW IF EXISTS util_all_probs_performance CASCADE")
    execute_query(f"CREATE VIEW util_all_probs_performance AS {query};")
    conn.commit()
    
def create_dubio_final_prob_view(table_name: str):
    baseline_query = f"SELECT id, prob(d.dict, _sentence) FROM {table_name} t JOIN _dict d ON d.name = 'thomasdict'"
    execute_query("DROP VIEW IF EXISTS util_final_dubio_prob CASCADE")
    execute_query(f"CREATE VIEW util_final_dubio_prob AS {baseline_query};")
    conn.commit()


def create_final_dual_relation_prob_view(table_getting_query: str):
    """
    Create a view that shows the final dual relation probabilities from a table.
    """
    execute_query("DROP VIEW IF EXISTS util_final_dual_relation_prob CASCADE")
    query = create_dual_relation_prob_query(table_getting_query)
    execute_query(f"CREATE VIEW util_final_dual_relation_prob AS {query};")
    conn.commit()

def create_final_triple_relation_prob_view(table_getting_query: str):
    """
    Create a view that shows the final triple relation probabilities from a table.
    """
    execute_query("DROP VIEW IF EXISTS util_final_triple_relation_prob CASCADE")
    query = create_triple_relation_prob_query(table_getting_query)
    execute_query(f"CREATE VIEW util_final_triple_relation_prob AS {query};")
    conn.commit()

def drop_all_util_views():
    """
    Drop all utility views.
    """
    execute_query("DROP VIEW IF EXISTS util_all_probs_performance CASCADE;")
    execute_query("DROP VIEW IF EXISTS util_final_dual_relation_prob CASCADE;")
    execute_query("DROP VIEW IF EXISTS util_final_triple_relation_prob CASCADE;")
    conn.commit()

#print_prob_dual_from_table("SELECT * FROM t_witnesses")
#print_prob_triple_from_table("SELECT * FROM t_witnesses")
#print_all_from_table("SELECT * FROM t_witnesses")
import re

def analyze_query_and_log_all(query: str, log_file: str, label: str = "Unnamed"):
    cur.execute(f"EXPLAIN ANALYZE {query}")
    rows = cur.fetchall()

    execution_time = None
    planning_time = None
    rows_returned = None
    loops = None

    for row in rows:
        line = row[0]

        # Extract execution time
        if "Execution Time" in line:
            match = re.search(r"Execution Time: ([\d\.]+) ms", line)
            if match:
                execution_time = float(match.group(1))

        # Extract planning time
        elif "Planning Time" in line:
            match = re.search(r"Planning Time: ([\d\.]+) ms", line)
            if match:
                planning_time = float(match.group(1))

        # Extract top-level rows and loops (usually the first line with 'rows=' and 'loops=')
        elif rows_returned is None and "rows=" in line and "loops=" in line:
            match = re.search(r"rows=(\d+)", line)
            if match:
                rows_returned = int(match.group(1))
            match = re.search(r"loops=(\d+)", line)
            if match:
                loops = int(match.group(1))

    # Log the extracted values
    with open(log_file, "a") as f:
        f.write(f"{label}\t{execution_time:.3f} ms\t{planning_time:.3f} ms\trows={rows_returned}\tloops={loops}\n")

    print(f"Logged: {label}\t{execution_time:.3f} ms\t{planning_time:.3f} ms\trows={rows_returned}\tloops={loops}")

table_getting_query = "SELECT * FROM t_witnesses"
query = create_dual_relation_prob_query("SELECT * FROM t_witnesses")
analyze_query_and_log_all(query, "timing_results.tsv", label="dual")

query = create_triple_relation_prob_query("SELECT * FROM t_witnesses")
analyze_query_and_log_all(query, "timing_results.tsv", label="triple")

baseline_query = "SELECT id, prob(d.dict, _sentence) FROM t_witnesses t JOIN _dict d ON d.name = 'thomasdict'"
analyze_query_and_log_all(baseline_query, "timing_results.tsv", label="native")
execute_query_print(f"SELECT COUNT(*) FROM ({create_dual_relation_prob_query(table_getting_query)}) AS final_dual")
execute_query_print(f"SELECT COUNT(*) FROM ({create_triple_relation_prob_query(table_getting_query)}) AS final_triple")

create_dubio_final_prob_view("t_witnesses")
create_final_dual_relation_prob_view("SELECT * FROM t_witnesses")
create_final_triple_relation_prob_view("SELECT * FROM t_witnesses")
create_all_probs_performance_view("SELECT * FROM t_witnesses")


# 6. Close cursor and connection
cur.close()
conn.close()

