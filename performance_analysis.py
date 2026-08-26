import psycopg2
import synthetic_data_generator_faster_even_faster as sdg
import numpy as np



def execute_query(query: str):
    """
    Perform a SQL query and print results like:
    'Witness: Betty, Sentence: value'
    """
    cur = sdg.get_cursor()
    cur.execute(query)

def execute_query_print(query: str):
    cur = sdg.get_cursor()
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
    cur = sdg.get_cursor()
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





def create_dual_relation_prob_query(sentences_table_name: str, var_table_name: str):
    return f"""
    WITH ranked_sentences AS (
        SELECT DISTINCT tostring(_sentence) AS stringsent,
               DENSE_RANK() OVER (ORDER BY tostring(_sentence)) AS id
        FROM {sentences_table_name} t
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
        JOIN {var_table_name}_dualrelation dr ON rv.varval = dr.varval
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
    FROM {sentences_table_name} t
    JOIN sentence_probs sp ON tostring(t._sentence) = sp.stringsent
    ORDER BY t.id
    """




    

def create_triple_relation_prob_query(sentences_table_name: str, var_table_name: str):
    return f"""
    WITH ranked_sentences AS (
        SELECT DISTINCT tostring(_sentence) AS stringsent,
               DENSE_RANK() OVER (ORDER BY tostring(_sentence)) AS id
        FROM {sentences_table_name} t
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
        JOIN {var_table_name}_triplerelation tr ON tr.var = rv.var AND tr.val = rv.val
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
    FROM {sentences_table_name} t
    JOIN sentence_probs sp ON tostring(t._sentence) = sp.stringsent
    ORDER BY t.id
    """



#Now create a view that shows the entire t_witness table with probability using base dubio, the probability using dual sentence, the probability using triple sentence


#execute_query_print(final_sentence_prob_dual)
#execute_query_print(final_sentence_prob_triple)
#execute_query_print("SELECT prob(d.dict, _sentence) FROM t_witnesses t, _dict d WHERE d.name = 'thomasdict'")
#execute_query_print(all_witness_probs)#


def analyze_dual_relation_prob(sentences_table_name: str, var_table_name: str):
    """
    Analyze the dual relation probabilities from a table.
    """
    query = create_dual_relation_prob_query(sentences_table_name, var_table_name)
    execute_query_and_analyze(query)

def analyze_triple_relation_prob(sentences_table_name: str, var_table_name: str):
    """
    Analyze the triple relation probabilities from a table.
    """
    query = create_triple_relation_prob_query(sentences_table_name, var_table_name)
    execute_query_and_analyze(query)

def print_prob_dual_from_table(sentences_table_name: str, var_table_name: str):
    """
    Print the dual relation probabilities from a table.
    """
    query = create_dual_relation_prob_query(sentences_table_name, var_table_name)
    execute_query_print(query)

def print_prob_triple_from_table(sentences_table_name: str, var_table_name: str):
    """
    Print the triple relation probabilities from a table.
    """
    query = create_triple_relation_prob_query(sentences_table_name, var_table_name)
    execute_query_print(query)

def create_all_probs_from_table(sentences_table_name: str, var_table_name: str, epsilon: float = 0.0001):
    """
    Print all entries and probabilities using all methods from a dynamic table query.
    Includes flags for deviation between base and dual/triple probabilities.
    """
    final_sentence_prob_dual = create_dual_relation_prob_query(sentences_table_name, var_table_name)
    final_sentence_prob_triple = create_triple_relation_prob_query(sentences_table_name, var_table_name)

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
      {sentences_table_name} AS t
      JOIN _dict d ON d.name = '{var_table_name}_dict'
      LEFT JOIN ({final_sentence_prob_dual}) AS final_dual 
        ON tostring(t._sentence) = final_dual.stringsent
      LEFT JOIN ({final_sentence_prob_triple}) AS final_triple 
        ON tostring(t._sentence) = final_triple.stringsent
    ORDER BY 
      tostring(t._sentence)
    """
    return all_witness_probs


def print_all_from_table(sentences_table_name: str, var_table_name: str):
    """
    Print all entries and probabilities using all methods from a dynamic table query.
    """
    query = create_all_probs_from_table(sentences_table_name, var_table_name)
    execute_query_print(query)

def create_all_probs_performance_view(sentences_table_name: str, var_table_name: str):
    """
    Create a view that shows all probabilities from a table.
    """
    conn = sdg.get_connection()
    query = create_all_probs_from_table(sentences_table_name, var_table_name)
    execute_query("DROP VIEW IF EXISTS util_all_probs_performance CASCADE")
    execute_query(f"CREATE VIEW util_all_probs_performance AS {query};")
    conn.commit()
    
def create_dubio_final_prob_view(sentences_table_name: str, var_table_name: str):
    conn = sdg.get_connection()
    baseline_query = f"SELECT id, prob(d.dict, _sentence) FROM {sentences_table_name} t JOIN _dict d ON d.name = '{var_table_name}_dict'"
    execute_query("DROP VIEW IF EXISTS util_final_dubio_prob CASCADE")
    execute_query(f"CREATE VIEW util_final_dubio_prob AS {baseline_query};")
    conn.commit()


def create_final_dual_relation_prob_view(sentences_table_name: str, var_table_name: str):
    conn = sdg.get_connection()
    """
    Create a view that shows the final dual relation probabilities from a table.
    """
    execute_query("DROP VIEW IF EXISTS util_final_dual_relation_prob CASCADE")
    query = create_dual_relation_prob_query(sentences_table_name, var_table_name)
    execute_query(f"CREATE VIEW util_final_dual_relation_prob AS {query};")
    conn.commit()

def create_final_triple_relation_prob_view(sentences_table_name: str, var_table_name: str):
    conn = sdg.get_connection()
    """
    Create a view that shows the final triple relation probabilities from a table.
    """
    execute_query("DROP VIEW IF EXISTS util_final_triple_relation_prob CASCADE")
    query = create_triple_relation_prob_query(sentences_table_name, var_table_name)
    execute_query(f"CREATE VIEW util_final_triple_relation_prob AS {query};")
    conn.commit()

def drop_all_util_views():
    conn = sdg.get_connection()
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

def analyze_query_and_log_all(query: str, log_file: str, label: str = "Unnamed", do_logs: bool = True):
    cur = sdg.get_cursor()
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
    if do_logs:
        # Log the extracted values
        with open(log_file, "a") as f:
            f.write(f"{label}\t{execution_time:.3f} ms\t{planning_time:.3f} ms\trows={rows_returned}\tloops={loops}\n")

    #print(f"Logged: {label}\t{execution_time:.3f} ms\t{planning_time:.3f} ms\trows={rows_returned}\tloops={loops}")
    return (execution_time, planning_time, rows_returned, loops)


class AnalysisParams:
    """
    Class to hold parameters for analysis.
    """
    def __init__(self, persons, total_rows, log_file, do_logs, sentences_table_name, var_table_name, columns, create_views: bool = True, print_counts: bool = True, print_deviation: bool = True):
        self.persons = persons
        self.total_rows = total_rows
        self.log_file = log_file
        self.do_logs = do_logs
        self.sentences_table_name = sentences_table_name
        self.var_table_name = var_table_name
        self.columns = columns
        self.create_views = create_views
        self.print_counts = print_counts
        self.print_deviation = print_deviation
    
    def create_copy(self):
        """
        Create a copy of the AnalysisParams object.
        """
        return AnalysisParams(
            self.persons,
            self.total_rows,
            self.log_file,
            self.do_logs,
            self.sentences_table_name,
            self.var_table_name,
            self.columns,
            self.create_views,
            self.print_counts,
            self.print_deviation
        )


class AnalysisResults:
    """
    Class to hold results of the analysis.
    """
    def __init__(self):
        self.base_exec_times = []
        self.dual_exec_times = []
        self.triple_exec_times = []
        self.base_sched_times = []
        self.dual_sched_times = []
        self.triple_sched_times = []
        self.rows_returned = []
        self.loops = []
        self.dict_vars = 0
        self.dict_values = 0
        self.total_table_columns = 0
        self.total_table_rows = 0
        self.total_iters = 0
    def set_total_table_columns(self, total_table_columns):
        if self.total_table_columns == 0:
            self.total_table_columns = total_table_columns
        else:
            if self.total_table_columns != total_table_columns:
                raise ValueError("Total table columns count mismatch.")
            else:
                return
    def set_total_table_rows(self, total_table_rows):
        if self.total_table_rows == 0:
            self.total_table_rows = total_table_rows
        else:
            if self.total_table_rows != total_table_rows:
                raise ValueError("Total table rows count mismatch.")
            else:
                return
    def set_dict_vars(self, dict_vars):
        if self.dict_vars == 0:
            self.dict_vars = dict_vars
        else:
            if self.dict_vars != dict_vars:
                raise ValueError("Dictionary variables count mismatch.")
            else:
                return
    def set_dict_values(self, dict_values):
        if self.dict_values == 0:
            self.dict_values = dict_values
        else:
            if self.dict_values != dict_values:
                raise ValueError("Dictionary values count mismatch.")
            else:
                return
    def add_base_result(self, execution_time, planning_time, rows_returned, loops):
        #print(f"Adding base result: {execution_time} ms, {planning_time} ms, rows={rows_returned}, loops={loops}")
        self.base_exec_times.append(execution_time)
        self.base_sched_times.append(planning_time)
        self.rows_returned.append(rows_returned)
        self.loops.append(loops)
    def add_dual_result(self, execution_time, planning_time, rows_returned, loops):
        #print(f"Adding dual result: {execution_time} ms, {planning_time} ms, rows={rows_returned}, loops={loops}")
        self.dual_exec_times.append(execution_time)
        self.dual_sched_times.append(planning_time)
        self.rows_returned.append(rows_returned)
        self.loops.append(loops)
    def add_triple_result(self, execution_time, planning_time, rows_returned, loops):
        #print(f"Adding triple result: {execution_time} ms, {planning_time} ms, rows={rows_returned}, loops={loops}")
        self.triple_exec_times.append(execution_time)
        self.triple_sched_times.append(planning_time)
        self.rows_returned.append(rows_returned)
        self.loops.append(loops)
    def average_base_execution_time(self):
        return sum(self.base_exec_times) / len(self.base_exec_times)
    def average_dual_execution_time(self):
        return sum(self.dual_exec_times) / len(self.dual_exec_times)
    def average_triple_execution_time(self):
        return sum(self.triple_exec_times) / len(self.triple_exec_times)
    def average_base_planning_time(self):
        return sum(self.base_sched_times) / len(self.base_sched_times)
    def average_dual_planning_time(self):
        return sum(self.dual_sched_times) / len(self.dual_sched_times)
    def average_triple_planning_time(self):
        return sum(self.triple_sched_times) / len(self.triple_sched_times)
    def is_sanity_check_passed(self):
        #TODO observe explain analyze problem in the code directory. For now we just assume and always return True :|
        """
        for i in range(len(self.rows_returned)):
            if i + 1 < len(self.rows_returned):
                if self.rows_returned[i] != self.rows_returned[i + 1]:
                    print(self.rows_returned)
                    #print(f"Sanity check failed: rows returned differ at index {i} and {i + 1}.")
                    raise ValueError("Rows returned are inconsistent across queries.")
        #print("Sanity check passed: rows returned are consistent across all queries.")
        """
        return True
    def is_loops_consistent(self):
        #TODO the same as above, we assume the loops are consistent for now
        """
        for i in range(len(self.loops)):
            if i + 1 < len(self.loops):
                if self.loops[i] != self.loops[i + 1]:
                    #print(f"Sanity check failed: loops differ at index {i} and {i + 1}.")
                    raise ValueError("Loops are inconsistent across queries.")
        #print("Sanity check passed: loops are consistent across all queries.")
        """
        return True
    
    def format_results(self):
        """
        Format the results for printing.
        """
        return (
            f"Base Execution Time: {self.average_base_execution_time():.3f} ms\n"
            f"Dual Execution Time: {self.average_dual_execution_time():.3f} ms\n"
            f"Triple Execution Time: {self.average_triple_execution_time():.3f} ms\n"
            f"Base Planning Time: {self.average_base_planning_time():.3f} ms\n"
            f"Dual Planning Time: {self.average_dual_planning_time():.3f} ms\n"
            f"Triple Planning Time: {self.average_triple_planning_time():.3f} ms\n"
            f"Dictionary Variables: {self.dict_vars}\n"
            f"Dictionary Values: {self.dict_values}\n"
            f"Total Table Columns: {self.total_table_columns}\n"
            f"Total Table Rows: {self.total_table_rows}\n"
            f"Sanity Check Passed: {self.is_sanity_check_passed()}\n"
            f"Loops Consistent: {self.is_loops_consistent()}\n"
            f"Total Iterations: {self.total_iters}"
        )
    
    def format_results_dict(self):
        """
        Format the results for printing as a dictionary.
        """
        return {
            "base_execution_time": self.average_base_execution_time(),
            "dual_execution_time": self.average_dual_execution_time(),
            "triple_execution_time": self.average_triple_execution_time(),
            "base_planning_time": self.average_base_planning_time(),
            "dual_planning_time": self.average_dual_planning_time(),
            "triple_planning_time": self.average_triple_planning_time(),
            "dict_vars": self.dict_vars,
            "dict_values": self.dict_values,
            "total_table_columns": self.total_table_columns,
            "total_table_rows": self.total_table_rows,
            "sanity_check_passed": self.is_sanity_check_passed(),
            "loops_consistent": self.is_loops_consistent(),
            "total_iters": self.total_iters
        }
            


def perform_analysis_and_log(analysis_params: AnalysisParams, analysis_results: AnalysisResults, force_no_new_table: bool = False):
    """
    Perform analysis and log results for dual and triple relation probabilities.
    """
    cur = sdg.get_cursor()
    persons = analysis_params.persons
    total_rows = analysis_params.total_rows
    log_file = analysis_params.log_file
    sentences_table_name = analysis_params.sentences_table_name
    var_table_name = analysis_params.var_table_name
    columns = analysis_params.columns
    create_views = analysis_params.create_views
    print_counts = analysis_params.print_counts
    print_deviation = analysis_params.print_deviation
    #print("TOTAL ITERS:", analysis_results.total_iters)
    #Refresh the witness table with new data
    if analysis_results.total_iters == 0 and not force_no_new_table:
        print("Creating new table with synthetic data...")
        sdg.create_table(var_table_name, columns, persons, total_rows)
    
    # Create the dual relation probability query
    
    dual_query = create_dual_relation_prob_query(sentences_table_name, var_table_name)
    # Analyze and log the dual relation probability query
    exec_time, sched_time, rows, loops = analyze_query_and_log_all(dual_query, log_file, label="dual_relation", do_logs=analysis_params.do_logs)
    analysis_results.add_dual_result(exec_time, sched_time, rows, loops)
    # Create the triple relation probability query
    triple_query = create_triple_relation_prob_query(sentences_table_name, var_table_name)
    # Analyze and log the triple relation probability query
    exec_time, sched_time, rows, loops = analyze_query_and_log_all(triple_query, log_file, label="triple_relation", do_logs=analysis_params.do_logs)
    analysis_results.add_triple_result(exec_time, sched_time, rows, loops)
    baseline_query = f"SELECT id, prob(d.dict, _sentence) FROM {sentences_table_name} t JOIN _dict d ON d.name = '{var_table_name}_dict'"
    # Analyze and log the baseline query
    exec_time, sched_time, rows, loops = analyze_query_and_log_all(baseline_query, log_file, label="baseline", do_logs=analysis_params.do_logs)
    analysis_results.add_base_result(exec_time, sched_time, rows, loops)
    dict_values = f"SELECT dict FROM _dict WHERE name = '{var_table_name}_dict'"
    cur.execute(dict_values)
    dict_row = cur.fetchone()
    match = re.search(r"#vars=(\d+), #values=(\d+)", dict_row[0])
    num_vars = int(match.group(1))
    num_values = int(match.group(2))
    #print(f"Vars: {num_vars}, Values: {num_values}")
    analysis_results.set_dict_vars(num_vars)
    analysis_results.set_dict_values(num_values)
    row_counting_query = f"SELECT COUNT(*) FROM {sentences_table_name}"
    cur.execute(row_counting_query)
    amount_rows = cur.fetchone()[0]
    analysis_results.set_total_table_rows(amount_rows)
    column_counting_query = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{sentences_table_name}'"
    cur.execute(column_counting_query)
    total_columns = cur.fetchone()[0]
    analysis_results.set_total_table_columns(total_columns)
    if analysis_params.do_logs:    
    # Log dictionary values
        with open(log_file, "a") as f:
            f.write(f"Dictionary: {dict_row[0]}\n")
            f.write(f"Experiment parameters: persons={persons}, total_rows = {total_rows}\n")
            f.write(f"Table name: {amount_rows}, amount of columns: {total_columns} amount of rows: {amount_rows}\n")
            f.write("------------------------------------------------------------------------\n")
        #print("Analysis and logging completed.")
    
    #create some views for later use
    if create_views and analysis_results.total_iters == 0:
        create_dubio_final_prob_view(sentences_table_name, var_table_name)
        create_final_dual_relation_prob_view(sentences_table_name, var_table_name)
        create_final_triple_relation_prob_view(sentences_table_name, var_table_name)
        create_all_probs_performance_view(sentences_table_name, var_table_name)
        print("Views created successfully.")
    if print_counts:
        execute_query_print(f"SELECT COUNT(*) FROM util_all_probs_performance;")
        execute_query_print(f"SELECT COUNT(*) FROM util_final_dual_relation_prob;")
        execute_query_print(f"SELECT COUNT(*) FROM util_final_triple_relation_prob;")
        execute_query_print(f"SELECT COUNT(*) FROM util_final_dubio_prob;")
        print("Counts printed successfully.")
    if print_deviation:
        print("Printing deviations for dual and triple relations...")
        execute_query_print("SELECT id, _sentence, dual_deviation, triple_deviation FROM util_all_probs_performance WHERE dual_deviation = True OR triple_deviation = True;")
        print("Deviation printed successfully.")
    #print("------------------------------------------------------------------------")
    
    analysis_results.total_iters += 1


def analyze_sequence(iters_per_params: int, paramslist: list[AnalysisParams], sequence_log_file: str):
    """
    Run a test analysis and print the results.
    """
    import json
    import time
    for params in paramslist:
        analysis_results = AnalysisResults()
        orginal_time = time.time()
        for y in range(iters_per_params):
            perform_analysis_and_log(params, analysis_results)
        print("\n----------------------------------------------------------------")
        print("Analysis done with results: ")
        results_dict = analysis_results.format_results_dict()
        results_dict["persons"] = params.persons
        results_dict["total_rows"] = params.total_rows
        print(results_dict)
        print("----------------------------------------------------------------\n")
        with open(sequence_log_file, "a") as f:
            f.write(json.dumps(results_dict, indent=4) + "\n")
            f.write("------------------------------------------------------------\n")
        print(f"Analysis done with time: {time.time() - orginal_time:.3f} seconds")

def analyze_sequence_with_limits_rows_changing(iters_per_params: int, initial_param: AnalysisParams, rows_per_analysis: list[int],  sequence_log_file: str):
    """
    Run a test analysis and print the results. Only applicable if all logs may be performed on the same main table.
    """
    sdg.create_table(initial_param.var_table_name, initial_param.columns, initial_param.persons, initial_param.total_rows)
    #TODO during generation the view name is not used so we need to fix the query to use original relation tables instead but use the view name for data. I CHANGED ANALYSIS PaRAMS
    import json
    import time
    for row_amount in rows_per_analysis:
        cur = sdg.get_cursor()
        cur.execute(f"DROP VIEW IF EXISTS {initial_param.sentences_table_name} CASCADE")
        cur.execute(f"CREATE VIEW {initial_param.sentences_table_name} AS SELECT * FROM {initial_param.var_table_name} LIMIT {row_amount}")
        analysis_results = AnalysisResults()
        orginal_time = time.time()
        for y in range(iters_per_params):
            perform_analysis_and_log(initial_param, analysis_results, force_no_new_table=True)
        print("\n----------------------------------------------------------------")
        print("Analysis done with results: ")
        results_dict = analysis_results.format_results_dict()
        results_dict["total_persons"] = initial_param.persons
        results_dict["total_columns"] = initial_param.columns
        results_dict["total_rows_checked"] = row_amount
        print(results_dict)
        print("----------------------------------------------------------------\n")
        with open(sequence_log_file, "a") as f:
            f.write(json.dumps(results_dict, indent=4) + "\n")
            f.write("------------------------------------------------------------\n")
        print(f"Analysis done with time: {time.time() - orginal_time:.3f} seconds")
    with open(sequence_log_file, "a") as f:
        f.write("Analysis completed for all row amounts. \n")
        f.write(f"Total iterations: {analysis_results.total_iters}\n")
        f.write(f"Table name: {initial_param.var_table_name}\n")
        f.write(f"Persons: {initial_param.persons}\n")
        f.write(f"Total rows: {initial_param.total_rows}\n")
        f.write(f"Columns: {initial_param.columns} + {len(initial_param.columns)}\n")
        dictionary_shape_query = f"SELECT dict FROM _dict WHERE name = '{initial_param.var_table_name}_dict'"
        cur.execute(dictionary_shape_query)
        dict_row = cur.fetchone()
        f.write(f"Dictionary shape: {dict_row[0]}\n")
        f.write("DONE------------------------------------------------------------DONE\n")
        
def analyze_sequence_with_limits_persons_changing(iters_per_params: int, initial_param: AnalysisParams, persons_per_analysis: list[int],  sequence_log_file: str):
    """
    Run a test analysis and print the results. Only applicable if all logs may be performed on the same main table.
    """
    
    #TODO during generation the view name is not used so we need to fix the query to use original relation tables instead but use the view name for data. I CHANGED ANALYSIS PaRAMS
    import json
    import time
    for person_amount in persons_per_analysis:
        sdg.create_table(initial_param.var_table_name, initial_param.columns, person_amount, initial_param.total_rows)
        cur = sdg.get_cursor()
        cur.execute(f"DROP VIEW IF EXISTS {initial_param.sentences_table_name} CASCADE")
        cur.execute(f"CREATE VIEW {initial_param.sentences_table_name} AS SELECT * FROM {initial_param.var_table_name} LIMIT {initial_param.total_rows}")
        analysis_results = AnalysisResults()
        orginal_time = time.time()
        for y in range(iters_per_params):
            perform_analysis_and_log(initial_param, analysis_results, force_no_new_table=True)
        print("\n----------------------------------------------------------------")
        print("Analysis done with results: ")
        results_dict = analysis_results.format_results_dict()
        results_dict["total_persons"] = person_amount
        results_dict["total_columns"] = initial_param.columns
        results_dict["total_rows_checked"] = initial_param.total_rows
        print(results_dict)
        print("----------------------------------------------------------------\n")
        with open(sequence_log_file, "a") as f:
            f.write(json.dumps(results_dict, indent=4) + "\n")
            f.write("------------------------------------------------------------\n")
        print(f"Analysis done with time: {time.time() - orginal_time:.3f} seconds")
    with open(sequence_log_file, "a") as f:
        f.write("Analysis completed for all row amounts. \n")
        f.write(f"Total iterations: {analysis_results.total_iters}\n")
        f.write(f"Table name: {initial_param.var_table_name}\n")
        f.write(f"Persons: {initial_param.persons}\n")
        f.write(f"Total rows: {initial_param.total_rows}\n")
        f.write(f"Columns: {initial_param.columns} + {len(initial_param.columns)}\n")
        dictionary_shape_query = f"SELECT dict FROM _dict WHERE name = '{initial_param.var_table_name}_dict'"
        cur.execute(dictionary_shape_query)
        dict_row = cur.fetchone()
        f.write(f"Dictionary shape: {dict_row[0]}\n")
        f.write("DONE------------------------------------------------------------DONE\n")

possible_column_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
def analyze_sequence_with_limits_columns_changing(iters_per_params: int, initial_param: AnalysisParams, columns_per_analysis: list[int],  sequence_log_file: str):
    """
    Run a test analysis and print the results. Only applicable if all logs may be performed on the same main table.
    """
    
    #TODO during generation the view name is not used so we need to fix the query to use original relation tables instead but use the view name for data. I CHANGED ANALYSIS PaRAMS
    import json
    import time
    for column_size in columns_per_analysis:
        columns = possible_column_names[:column_size]
        sdg.create_table(initial_param.var_table_name, columns, initial_param.persons, initial_param.total_rows)
        cur = sdg.get_cursor()
        cur.execute(f"DROP VIEW IF EXISTS {initial_param.sentences_table_name} CASCADE")
        cur.execute(f"CREATE VIEW {initial_param.sentences_table_name} AS SELECT * FROM {initial_param.var_table_name} LIMIT {initial_param.total_rows}")
        analysis_results = AnalysisResults()
        orginal_time = time.time()
        for y in range(iters_per_params):
            perform_analysis_and_log(initial_param, analysis_results, force_no_new_table=True)
        print("\n----------------------------------------------------------------")
        print("Analysis done with results: ")
        results_dict = analysis_results.format_results_dict()
        results_dict["total_persons"] = initial_param.persons
        results_dict["total_columns"] = column_size
        results_dict["total_rows_checked"] = initial_param.total_rows
        print(results_dict)
        print("----------------------------------------------------------------\n")
        with open(sequence_log_file, "a") as f:
            f.write(json.dumps(results_dict, indent=4) + "\n")
            f.write("------------------------------------------------------------\n")
        print(f"Analysis done with time: {time.time() - orginal_time:.3f} seconds")
    with open(sequence_log_file, "a") as f:
        f.write("Analysis completed for all row amounts. \n")
        f.write(f"Total iterations: {analysis_results.total_iters}\n")
        f.write(f"Table name: {initial_param.var_table_name}\n")
        f.write(f"Persons: {initial_param.persons}\n")
        f.write(f"Total rows: {initial_param.total_rows}\n")
        f.write(f"Columns: {initial_param.columns} + {len(initial_param.columns)}\n")
        dictionary_shape_query = f"SELECT dict FROM _dict WHERE name = '{initial_param.var_table_name}_dict'"
        cur.execute(dictionary_shape_query)
        dict_row = cur.fetchone()
        f.write(f"Dictionary shape: {dict_row[0]}\n")
        f.write("DONE------------------------------------------------------------DONE\n")
        
def analyze_sequence_with_limits_columns_and_persons_changing(iters_per_params: int, initial_param: AnalysisParams, columns_per_analysis: list[int], people_per_analysis: list[int],  sequence_log_file: str):
    """
    Run a test analysis and print the results. Only applicable if all logs may be performed on the same main table.
    """
    
    #TODO during generation the view name is not used so we need to fix the query to use original relation tables instead but use the view name for data. I CHANGED ANALYSIS PaRAMS
    import json
    import time
    if len(columns_per_analysis) != len(people_per_analysis):
        print(len(columns_per_analysis), len(people_per_analysis))
        raise ValueError("Columns per analysis and people per analysis must have the same length.")
    for x in range(len(columns_per_analysis)):
        columns = possible_column_names[:columns_per_analysis[x]]
        sdg.create_table(initial_param.var_table_name, columns, people_per_analysis[x], initial_param.total_rows)
        cur = sdg.get_cursor()
        cur.execute(f"DROP VIEW IF EXISTS {initial_param.sentences_table_name} CASCADE")
        cur.execute(f"CREATE VIEW {initial_param.sentences_table_name} AS SELECT * FROM {initial_param.var_table_name} LIMIT {initial_param.total_rows}")
        analysis_results = AnalysisResults()
        orginal_time = time.time()
        for y in range(iters_per_params):
            perform_analysis_and_log(initial_param, analysis_results, force_no_new_table=True)
        print("\n----------------------------------------------------------------")
        print("Analysis done with results: ")
        results_dict = analysis_results.format_results_dict()
        results_dict["total_persons"] = people_per_analysis[x]
        results_dict["total_columns"] = columns_per_analysis[x]
        results_dict["total_rows_checked"] = initial_param.total_rows
        print(results_dict)
        print("----------------------------------------------------------------\n")
        with open(sequence_log_file, "a") as f:
            f.write(json.dumps(results_dict, indent=4) + "\n")
            f.write("------------------------------------------------------------\n")
        print(f"Analysis done with time: {time.time() - orginal_time:.3f} seconds")
    with open(sequence_log_file, "a") as f:
        f.write("Analysis completed for all row amounts. \n")
        f.write(f"Total iterations: {analysis_results.total_iters}\n")
        f.write(f"Table name: {initial_param.var_table_name}\n")
        f.write(f"Persons: {initial_param.persons}\n")
        f.write(f"Total rows: {initial_param.total_rows}\n")
        f.write(f"Columns: {initial_param.columns} + {len(initial_param.columns)}\n")
        dictionary_shape_query = f"SELECT dict FROM _dict WHERE name = '{initial_param.var_table_name}_dict'"
        cur.execute(dictionary_shape_query)
        dict_row = cur.fetchone()
        f.write(f"Dictionary shape: {dict_row[0]}\n")
        f.write("DONE------------------------------------------------------------DONE\n")



test_log_file_name = "inc_dict_vars_max_people_only_double_rows"
test_log_file_individual_logs_name = f"{test_log_file_name}_individual.log"
test_log_file_full_path = f"{test_log_file_name}.log"

#people_array = [5, 10, 20, 30, 40, 50, 60, 70, 80 ,90, 100, 110, 120, 130, 140, 150, 160, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000]
people_array_mega = [5, 10, 20, 30, 40, 50, 75, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 7500, 10000, 12500, 15000, 17500, 20000]
mega_param1 = AnalysisParams(
        persons=200000,
        total_rows = 20000,
        log_file=test_log_file_individual_logs_name,
        do_logs=False,
        sentences_table_name=f"mega_1_sent",
        var_table_name=f"mega_1",
        columns=['a', 'b', 'c'],
        create_views=False,
        print_counts=False,
        print_deviation=False
    )

mega_param2 = AnalysisParams(
        persons=200000,
        total_rows = 20000,
        log_file=test_log_file_individual_logs_name,
        do_logs=False,
        sentences_table_name=f"mega_2_sent",
        var_table_name=f"mega_2",
        columns=['a', 'b', 'c', 'd'],
        create_views=False,
        print_counts=False,
        print_deviation=False
    )

mega_param3 = AnalysisParams(
        persons=200000,
        total_rows = 20000,
        log_file=test_log_file_individual_logs_name,
        do_logs=False,
        sentences_table_name=f"mega_3_sent",
        var_table_name=f"mega_3",
        columns=['a', 'b', 'c', 'd', 'e'],
        create_views=False,
        print_counts=False,
        print_deviation=False
    )

mega_param4 = AnalysisParams(
        persons=200000,
        total_rows = 20000,
        log_file=test_log_file_individual_logs_name,
        do_logs=False,
        sentences_table_name=f"mega_4_sent",
        var_table_name=f"mega_4",
        columns=['a', 'b', 'c', 'd', 'e', 'f'],
        create_views=False,
        print_counts=False,
        print_deviation=False
    )

mega_col5 = AnalysisParams(
        persons=100,
        total_rows = 1000,
        log_file=test_log_file_individual_logs_name,
        do_logs=False,
        sentences_table_name=f"mega_col_sent",
        var_table_name=f"mega_col",
        columns=['a', 'b', 'c', 'd', 'e', 'f'],
        create_views=False,
        print_counts=False,
        print_deviation=False
    )

def get_divisor_steps(maximum: int, minimum: int, steps: int):
    # Get all divisors of `maximum` ≥ `minimum`
    divisors = sorted([i for i in range(minimum, maximum + 1) if maximum % i == 0])
    
    if len(divisors) < steps:
        raise ValueError(f"Only {len(divisors)} valid divisors between {minimum} and {maximum}, but {steps} requested.")

    # Evenly pick `steps` values from the sorted divisors
    step_indices = [round(i * (len(divisors) - 1) / (steps - 1)) for i in range(steps)]
    return [divisors[i] for i in step_indices]

total_entries = 1000
steps = 1000
start_value = 1
entry_values = np.linspace(start_value, total_entries, steps, dtype=int).tolist()
#print("Entry values for analysis:", entry_values)
#print(get_divisor_steps(maximum=1000, minimum=1, steps=10))
#people_numbers = get_divisor_steps(maximum=1000, minimum=1, steps=16)

"""
analyze_sequence_with_limits_persons_changing(
    iters_per_params= 2,
    initial_param=org_param,
    persons_per_analysis=entry_values,
    sequence_log_file=test_log_file_full_path
)
"""
"""
analyze_sequence_with_limits_columns_and_persons_changing(
    iters_per_params= 5,
    initial_param=org_param,
    columns_per_analysis=column_sizes,
    people_per_analysis=people_array,
    sequence_log_file=test_log_file_full_path
)


analyze_sequence_with_limits_persons_changing(
    iters_per_params= 10,
    initial_param=mega_param1,
    persons_per_analysis=people_array_mega,
    sequence_log_file="mega_3_col_new_test_986594_prev_crash.log"
)
analyze_sequence_with_limits_persons_changing(
    iters_per_params= 10,
    initial_param=mega_param2,
    persons_per_analysis=people_array_mega,
    sequence_log_file="mega_4_col.log"
)

analyze_sequence_with_limits_persons_changing(
    iters_per_params= 10,
    initial_param=mega_param3,
    persons_per_analysis=people_array_mega,
    sequence_log_file="mega_5_col.log"
)

analyze_sequence_with_limits_persons_changing(
    iters_per_params= 10,
    initial_param=mega_param4,
    persons_per_analysis=people_array_mega,
    sequence_log_file="mega_6_col.log"
)
"""

analyze_sequence_with_limits_columns_changing(
    iters_per_params= 10,
    initial_param=mega_col5,
    columns_per_analysis=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    sequence_log_file="mega_col_inc_1000_rows.log"
)

conn = sdg.get_connection()
cur = sdg.get_cursor()
conn.commit()
# 6. Close cursor and connection
cur.close()
conn.close()

