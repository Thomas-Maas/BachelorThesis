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

printdict = "SELECT print(d.dict) FROM _dict d WHERE d.name = 'thomasdict'"
execute_query_print(printdict)

prob = "SELECT t.name, t.color, t.car, t.time, prob(d.dict, _sentence) FROM t_witnesses t, _dict d WHERE d.name = 'thomasdict'"
#execute_query_print(prob)

# 1. Get all sentences from the relevant table
get_sentence_string = "SELECT tostring(_sentence) as stringsent FROM t_witnesses t"
execute_query_print(get_sentence_string)
# 2.1. Get all variables that occur in a sentence, give the sentence an ID and match appropriate variables to this ID
get_dual_sentence_vars = f"SELECT ranked_sentences.id, varval FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM t_witnesses) AS ranked_sentences, LATERAL regexp_split_to_table(ranked_sentences.stringsent, '[()&!|]+') AS varval WHERE varval <> '' AND varval <> '1' UNION SELECT ranked.id, '1' AS varval FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM t_witnesses WHERE tostring(_sentence) = '1') AS ranked"


execute_query("DROP VIEW IF EXISTS dual_sentence_vars CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW dual_sentence_vars AS {get_dual_sentence_vars}")
# 2.2. Get all variables that occur in a sentence, give the sentence an ID and match appropriate variables to this ID, split on =, to make this a triple relation
get_triple_sentence_vars = f"SELECT ranked_sentences.id, matches[1] AS var, matches[2]::int AS val FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM t_witnesses) AS ranked_sentences, LATERAL regexp_split_to_table(ranked_sentences.stringsent, '[()&!|]+') AS val, LATERAL regexp_matches(val, '^([a-zA-Z0-9]+)=([0-9]+)$') AS matches WHERE val <> '' AND val <> '1' UNION SELECT ranked.id, '1' AS var, 1 AS val FROM (SELECT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM t_witnesses WHERE tostring(_sentence) = '1') AS ranked"

execute_query("DROP VIEW IF EXISTS triple_sentence_vars CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW triple_sentence_vars AS {get_triple_sentence_vars}")
#Remove parentheses and ampersands from the sentence string, take distinct values, only non 1 or nonempty values
extract_relevant_duo_vars = f"""SELECT DISTINCT varval 
                        FROM ({get_sentence_string}) as ss, 
                        LATERAL regexp_split_to_table(ss.stringsent, '[()&!|]+') AS varval 
                        WHERE varval <> '1' AND varval <> '' ORDER BY varval"""
# Join the variables' probabilities on the UNIQUE table of variables  (varval, prob) e.g. (a1=2, 0.5)
join_probability_on_duo_vars = f"""SELECT rdv.varval, dr.prob FROM ({extract_relevant_duo_vars}) as rdv JOIN dualrelation dr ON rdv.varval = dr.varval"""
#create view showing the unique variables
execute_query("DROP VIEW IF EXISTS dualrelationvarsprob CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW dualrelationvarsprob AS {join_probability_on_duo_vars}")
# We will now construct a dummy dictionary to hold all unique variables and their probabilities using the dual relation variable table. If the variables values do not add up to 1, create a dummy variable with the remaining probability. Dummy value is max value + 1


#Utility function that creates a Dubio dict from a table of (varval, prob) tuples
create_dict_from_dual = f"""
SELECT 
  print(dictionary(string_agg(varval || ':' || prob::text, '; ') || ';')) AS final_dictionaryaaa
FROM ({join_probability_on_duo_vars}) AS final;
"""
execute_query_print(create_dict_from_dual)



#Remove parentheses and ampersands from the sentence string, take distinct values, only non 1 or nonempty values, split on =
extract_relevalt_triple_vars = f"""SELECT DISTINCT matches[1] as var, matches[2]::int as val 
                            FROM ({get_sentence_string}) as ss, LATERAL regexp_split_to_table(ss.stringsent, '[()&!|]+') AS val,
                            LATERAL regexp_matches(val, '^([a-zA-Z0-9]+)=([0-9]+)$') AS matches 
                            WHERE val <> '' ORDER BY var, val"""
# Join the variables' probabilities on the UNIQUE table of variables  (var, val, prob) e.g. (a1, 2, 0.5)
join_probability_on_triple_vars = f"""SELECT rtv.var, rtv.val, tr.prob FROM ({extract_relevalt_triple_vars}) as rtv JOIN triplerelation tr ON rtv.var = tr.var AND rtv.val = tr.val"""
execute_query("DROP VIEW IF EXISTS triplerelationvarsprob CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW triplerelationvarsprob AS {join_probability_on_triple_vars}")


#Utility function that creates a Dubio dict from a table of (var, val, prob) tuples
create_dict_from_triple = f"""
SELECT 
  print(dictionary(string_agg(var || '=' || val || ':' || prob::text, '; ') || ';')) AS final_dictionaryaaa
FROM ({join_probability_on_triple_vars}) AS final;
"""
execute_query_print(create_dict_from_triple)
#TODO Make it so that a table where all values of a var dont add up to 1, a dummy variable is created with the remaining probability. Dummy value is max value + 1 and probability of 1- sum(prob)


#For the entire table find replace variables with their probability value found in UNIQUE relevant probility table (named dualrelationvarsprob as a view above)
grouped_sentences_dual_prob_join = f"SELECT dsv.id, CASE WHEN dsv.varval = '1' THEN 1.0 ELSE drvp.prob END AS prob FROM ({get_dual_sentence_vars}) AS dsv LEFT JOIN ({join_probability_on_duo_vars}) drvp ON dsv.varval = drvp.varval"

execute_query("DROP VIEW IF EXISTS join_prob_on_dual_relation CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW join_prob_on_dual_relation AS {grouped_sentences_dual_prob_join}")
#For the entire table find replace variables with their probability value found in UNIQUE relevant probility table (named triplerelationvarsprob as a view above)
grouped_sentences_triple_prob_join = f"SELECT tsv.id, CASE WHEN tsv.var = '1' AND tsv.val = 1 THEN 1.0 ELSE trvp.prob END AS prob FROM ({get_triple_sentence_vars}) AS tsv LEFT JOIN ({join_probability_on_triple_vars}) trvp ON tsv.var = trvp.var AND tsv.val = trvp.val"

execute_query("DROP VIEW IF EXISTS join_prob_on_triple_relation CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW join_prob_on_triple_relation AS {grouped_sentences_triple_prob_join}")
#Now group by ID for both dual and triple relations, aggregate probability values by multiplying them
grouped_dual_prob = f"SELECT idprobs.id, exp(sum(ln(idprobs.prob))) as prob FROM ({grouped_sentences_dual_prob_join}) as idprobs GROUP BY idprobs.id ORDER BY idprobs.id"
execute_query("DROP VIEW IF EXISTS grouped_dual_prob CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW grouped_dual_prob AS {grouped_dual_prob}")
grouped_triple_prob = f"SELECT idprobs.id, exp(sum(ln(idprobs.prob))) as prob FROM ({grouped_sentences_triple_prob_join}) as idprobs GROUP BY idprobs.id ORDER BY idprobs.id"
execute_query("DROP VIEW IF EXISTS grouped_triple_prob CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW grouped_triple_prob AS {grouped_triple_prob}")
#Re input sentence instead of ID, so that we can see the sentence and its probability. For dual relations:
final_sentence_prob_dual = f"SELECT ranked_sentences.stringsent, gdp.prob FROM (SELECT DISTINCT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM t_witnesses) AS ranked_sentences JOIN ({grouped_dual_prob}) AS gdp ON ranked_sentences.id = gdp.id ORDER BY ranked_sentences.id"



final_sentence_prob_triple = f"SELECT ranked_sentences.stringsent, gtp.prob FROM (SELECT DISTINCT tostring(_sentence) AS stringsent, dense_rank() OVER (ORDER BY tostring(_sentence)) AS id FROM t_witnesses) AS ranked_sentences JOIN ({grouped_triple_prob}) AS gtp ON ranked_sentences.id = gtp.id ORDER BY ranked_sentences.id"



execute_query("DROP VIEW IF EXISTS final_sentence_prob_dual CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW final_sentence_prob_dual AS {final_sentence_prob_dual}")
execute_query("DROP VIEW IF EXISTS final_sentence_prob_triple CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW final_sentence_prob_triple AS {final_sentence_prob_triple}")

#Now create a view that shows the entire t_witness table with probability using base dubio, the probability using dual sentence, the probability using triple sentence
all_witness_probs = f"""
SELECT 
  t.id, 
  t.name, 
  t.color, 
  t.car, 
  t.time, 
  t._sentence,
  CASE 
    WHEN tostring(t._sentence) = '1' THEN 1
    ELSE prob(d.dict, t._sentence)
  END AS base_prob,
  COALESCE(final_dual.prob, 1) AS dual_prob,
  COALESCE(final_triple.prob, 1) AS triple_prob
FROM 
  t_witnesses t
  JOIN _dict d ON d.name = 'thomasdict'
  LEFT JOIN final_sentence_prob_dual final_dual 
    ON tostring(t._sentence) = final_dual.stringsent
  LEFT JOIN final_sentence_prob_triple final_triple 
    ON tostring(t._sentence) = final_triple.stringsent
ORDER BY 
  t.id, t.name, t.color, t.car, t.time;
"""

execute_query("DROP VIEW IF EXISTS all_witness_probs CASCADE;")
execute_query(f"CREATE OR REPLACE VIEW all_witness_probs AS {all_witness_probs}")
execute_query_print("SELECT print(dictionary(''))")


def drop_all_views():
    """
    Drop all views created in this script.
    """
    views = [
        "dualrelationvarsprob",
        "triplerelationvarsprob",
        "join_prob_on_dual_relation",
        "join_prob_on_triple_relation",
        "grouped_dual_prob",
        "grouped_triple_prob",
        "final_sentence_prob_dual",
        "final_sentence_prob_triple",
        "all_witness_probs",
        "dual_sentence_vars",
        "triple_sentence_vars",
    ]
    for view in views:
        cur.execute(f"DROP VIEW IF EXISTS {view} CASCADE;")

drop_all_views()



conn.commit()
# 6. Close cursor and connection
cur.close()
conn.close()

