import os
import psycopg2
import synthetic_data_generator as sdg
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
    return f"""
    WITH ranked_sentences AS (
        SELECT DISTINCT tostring(_sentence) AS stringsent,
               DENSE_RANK() OVER (ORDER BY tostring(_sentence)) AS id
        FROM ({table_getting_query}) AS t
    ),
    sentence_vars AS (
        SELECT rs.id, varval
        FROM ranked_sentences rs,
             LATERAL regexp_split_to_table(rs.stringsent, '[()&!|]+') AS varval
        WHERE varval <> '' AND varval <> '1'
        UNION
        SELECT rs.id, '1'
        FROM ranked_sentences rs
        WHERE rs.stringsent = '1'
    ),
    relevant_vars AS (
        SELECT DISTINCT varval
        FROM ranked_sentences rs,
             LATERAL regexp_split_to_table(rs.stringsent, '[()&!|]+') AS varval
        WHERE varval <> '' AND varval <> '1'
    ),
    var_probs AS (
        SELECT rv.varval, dr.prob
        FROM relevant_vars rv
        JOIN dualrelation dr ON rv.varval = dr.varval
    ),
    joined_probs AS (
        SELECT sv.id,
               CASE WHEN sv.varval = '1' THEN 1.0 ELSE vp.prob END AS prob
        FROM sentence_vars sv
        LEFT JOIN var_probs vp ON sv.varval = vp.varval
    ),
    grouped_probs AS (
        SELECT id, EXP(SUM(LN(prob))) AS prob
        FROM joined_probs
        GROUP BY id
    ),
    sentence_probs AS (
        SELECT rs.stringsent, gp.prob
        FROM ranked_sentences rs
        JOIN grouped_probs gp ON rs.id = gp.id
    )
    SELECT t.id, tostring(t._sentence) as stringsent, sp.prob
    FROM ({table_getting_query}) AS t
    JOIN sentence_probs sp ON tostring(t._sentence) = sp.stringsent
    ORDER BY t.id
    """




    

def create_triple_relation_prob_query(table_getting_query: str):
    return f"""
    WITH ranked_sentences AS (
        SELECT DISTINCT tostring(_sentence) AS stringsent,
               DENSE_RANK() OVER (ORDER BY tostring(_sentence)) AS id
        FROM ({table_getting_query}) AS t
    ),
    sentence_vars AS (
        SELECT rs.id, matches[1] AS var, matches[2]::int AS val
        FROM ranked_sentences rs,
             LATERAL regexp_split_to_table(rs.stringsent, '[()&!|]+') AS val,
             LATERAL regexp_matches(val, '^([a-zA-Z0-9]+)=([0-9]+)$') AS matches
        WHERE val <> '' AND val <> '1'
        UNION
        SELECT rs.id, '1', 1
        FROM ranked_sentences rs
        WHERE rs.stringsent = '1'
    ),
    relevant_vars AS (
        SELECT DISTINCT matches[1] AS var, matches[2]::int AS val
        FROM ranked_sentences rs,
             LATERAL regexp_split_to_table(rs.stringsent, '[()&!|]+') AS val,
             LATERAL regexp_matches(val, '^([a-zA-Z0-9]+)=([0-9]+)$') AS matches
        WHERE val <> '' AND val <> '1'
    ),
    var_probs AS (
        SELECT rv.var, rv.val, tr.prob
        FROM relevant_vars rv
        JOIN triplerelation tr ON tr.var = rv.var AND tr.val = rv.val
    ),
    joined_probs AS (
        SELECT sv.id,
               CASE WHEN sv.var = '1' AND sv.val = 1 THEN 1.0 ELSE vp.prob END AS prob
        FROM sentence_vars sv
        LEFT JOIN var_probs vp ON sv.var = vp.var AND sv.val = vp.val
    ),
    grouped_probs AS (
        SELECT id, EXP(SUM(LN(prob))) AS prob
        FROM joined_probs
        GROUP BY id
    ),
    sentence_probs AS (
        SELECT rs.stringsent, gp.prob
        FROM ranked_sentences rs
        JOIN grouped_probs gp ON rs.id = gp.id
    )
    SELECT t.id, tostring(t._sentence) as stringsent, sp.prob
    FROM ({table_getting_query}) AS t
    JOIN sentence_probs sp ON tostring(t._sentence) = sp.stringsent
    ORDER BY t.id
    """



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

def create_all_probs_from_table(table_getting_query: str, epsilon: float = 0.0001):
    """
    Print all entries and probabilities using all methods from a dynamic table query.
    Includes flags for deviation between base and dual/triple probabilities.
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
      COALESCE(final_triple.prob, 1) AS triple_prob,

      -- Deviation flag for dual
      CASE 
        WHEN ABS(COALESCE(final_dual.prob, 1) - 
                 CASE WHEN tostring(t._sentence) = '1' THEN 1 ELSE prob(d.dict, t._sentence) END) > {epsilon}
        THEN TRUE ELSE FALSE
      END AS dual_deviation,

      -- Deviation flag for triple
      CASE 
        WHEN ABS(COALESCE(final_triple.prob, 1) - 
                 CASE WHEN tostring(t._sentence) = '1' THEN 1 ELSE prob(d.dict, t._sentence) END) > {epsilon}
        THEN TRUE ELSE FALSE
      END AS triple_deviation

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
    execute_query("DROP VIEW IF EXISTS util_final_dubio_prob CASCADE")
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


def perform_analysis_and_log(persons, min_entries, max_entries, log_file, table_name, generate_data=True):
    """
    Perform analysis and log results for dual and triple relation probabilities.
    """
    #Refresh the witness table with new data
    if generate_data:
        sdg.create_witness_table(persons, min_entries, max_entries)
    
    # Create the dual relation probability query
    dual_query = create_dual_relation_prob_query(f"SELECT * FROM {table_name}")
    # Analyze and log the dual relation probability query
    analyze_query_and_log_all(dual_query, log_file, label="dual_relation")
    # Create the triple relation probability query
    triple_query = create_triple_relation_prob_query(f"SELECT * FROM {table_name}")
    # Analyze and log the triple relation probability query
    analyze_query_and_log_all(triple_query, log_file, label="triple_relation")
    baseline_query = f"SELECT id, prob(d.dict, _sentence) FROM {table_name} t JOIN _dict d ON d.name = 'thomasdict'"
    # Analyze and log the baseline query
    analyze_query_and_log_all(baseline_query, log_file, label="baseline")
    dict_values = "SELECT dict FROM _dict WHERE name = 'thomasdict'"
    # Log dictionary values
    with open(log_file, "a") as f:
        cur.execute(dict_values)
        dict_row = cur.fetchone()
        if dict_row:
            f.write(f"Dictionary: {dict_row[0]}\n")
            print(f"Dictionary: {dict_row[0]}")
        else:
            f.write("Dictionary: None\n")
            print("Dictionary: None")
        f.write(f"Experiment parameters: persons={persons}, min_entries={min_entries}, max_entries={max_entries}\n")
        f.write("------------------------------------------------------------------------\n")
    print("Analysis and logging completed.")
    
    #create some views for later use
    create_views = True
    if create_views:
        create_dubio_final_prob_view(table_name)
        create_final_dual_relation_prob_view("SELECT * FROM " + table_name)
        create_final_triple_relation_prob_view("SELECT * FROM " + table_name)
        create_all_probs_performance_view("SELECT * FROM " + table_name)
        print("Views created successfully.")
    print_counts = True
    if print_counts:
        execute_query_print(f"SELECT COUNT(*) FROM util_all_probs_performance;")
        execute_query_print(f"SELECT COUNT(*) FROM util_final_dual_relation_prob;")
        execute_query_print(f"SELECT COUNT(*) FROM util_final_triple_relation_prob;")
        execute_query_print(f"SELECT COUNT(*) FROM util_final_dubio_prob;")
        print("Counts printed successfully.")
    print_deviation = True
    if print_deviation:
        execute_query_print("SELECT id, _sentence, dual_deviation, triple_deviation FROM util_all_probs_performance WHERE dual_deviation = True OR triple_deviation = True;")
        print("Deviation printed successfully.")
    print("------------------------------------------------------------------------")
"""
take_first_five_sentences = "SELECT id, _sentence FROM t_witnesses LIMIT 5;"
execute_query(f"DROP VIEW IF EXISTS util_first_five_sentences CASCADE;")
execute_query(f"CREATE VIEW util_first_five_sentences AS {take_first_five_sentences};")

perform_analysis_and_log(
    persons=5,
    min_entries=10,
    max_entries=30,
    log_file="performance_analysis.log",
    table_name="util_first_five_sentences",
    generate_data=False
    
)
"""

perform_analysis_and_log(
    persons=206,
    min_entries=50,
    max_entries=200,
    log_file="performance_analysis.log",
    table_name="t_witnesses"
)

conn.commit()
# 6. Close cursor and connection
cur.close()
conn.close()

