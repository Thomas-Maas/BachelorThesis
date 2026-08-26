import os
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Tuple, Dict
import random
from enum import Enum
from dotenv import load_dotenv
from random_values import get_available_witness_id_name, get_available_suspect_id_name, get_random_car_color, get_random_car_type, get_random_time_of_day, get_random_bogus, reset_names

load_dotenv()

conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"]
)

import random

def generate_proportions(number):
    if number == 1 or number == 0:
        return [1.0]

    # Step 1: Use descending integers to keep proportions simple and decreasing
    raw = list(range(number, 0, -1))

    # Step 2: Normalize to sum to 1.0
    total = sum(raw)
    normalized = [x / total for x in raw]

    # Step 3: Round to 4 decimals for reasonable precision
    rounded = [round(x, 4) for x in normalized]

    # Step 4: Fix discrepancy by adjusting the largest value
    discrepancy = round(1.0 - sum(rounded), 4)
    max_index = rounded.index(max(rounded))
    rounded[max_index] = round(rounded[max_index] + discrepancy, 4)

    # Final checks
    assert all(v > 0 for v in rounded), "All values must be > 0"
    assert round(sum(rounded), 10) == 1.0, f"Sum must be exactly 1.0, got {sum(rounded)}"
    #print(rounded)
    return rounded






class Bdd_sentence_maker:
    def __init__(self, id: str, columns=list):
        self.id = id
       
        self.columns = columns  # list of column names
        self.typevalues = {col: [] for col in columns}  # Initialize typevalues with empty lists for each column
        self.variable_counts = {}
    
    def input_value(self, value: str, value_type: str):
        if value_type not in self.typevalues:
            self.typevalues[value_type] = []
        if value not in self.typevalues[value_type]:
            #print(f"Adding value '{value}' of type '{value_type}' to BDD sentence maker with id {self.id}")
            self.typevalues[value_type].append(value)
    
    def get_sentence(self, value_type: str, value: str) -> str:

        """
        Returns a BDD sentence for the given value and type.
        """
        variable = f"{value_type}{self.id}"
        if value_type not in self.typevalues:
            raise ValueError(f"Value type {value_type} not found during sentence getting.")
        #print(f"Getting sentence for {value_type} with value {value}, id: {self.id}")
        #print(f"Typevalues for {value_type}: {self.typevalues[value_type]}")
        value_index = self.typevalues[value_type].index(value)

        if len(self.typevalues[value_type]) <= 1:
            return "1"
        return f"{variable}={value_index}"
    
    
    def get_total_sentence(self, **kwargs) -> str:
        """
        Returns a combined BDD sentence for all specified column-value pairs.
        Example: get_total_sentence(color="red", car="sedan", ...)
        """
        expected_keys = self.columns
        for key in expected_keys:
            if key not in kwargs:
                raise ValueError(f"Missing value for '{key}' in get_total_sentence()")

        #print(f"Getting total sentence for {kwargs}, id: {self.id}")
        #print(f"Expected keys: {expected_keys}")
        sentences = [self.get_sentence(col, kwargs[col]) for col in expected_keys]
        #print(f"Generated sentences: {sentences}")
        return "&".join(sentences)
    
    def print_variable_counts(self):
        """
        Prints the variable counts.
        """
        for variable, count in self.variable_counts.items():
            print(f"{variable}: {count}")
    
    def get_variable_counts(self):
        """
        Returns the variable counts.
        """
        for value_type, values in self.typevalues.items():
            self.variable_counts[f"{value_type}{self.id}"] = len(values)
        #print(f"Variable counts for {self.id}: {self.variable_counts}")
        return self.variable_counts 


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
        #print(", ".join(parts))

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

def get_connection():
    """
    Get the current database connection and cursor.
    """
    return conn
def get_cursor():
    """
    Get the current database cursor.
    """
    return cur



from typing import List, Dict, Tuple
import time

def insert_person_data(entry_count: int, columns: list) -> Tuple[List[Tuple], List[Tuple], List[Tuple]]:
    import random
    id, name = get_available_witness_id_name()
    org_time = time.time()

    entry = []
    for _ in range(entry_count):
        row = tuple(get_random_bogus() for _ in columns)
        if row not in entry:
            entry.append(row)

    #print(f"Took {time.time() - org_time:.2f} seconds to generate {len(entry)} entries for {name} with id {id}")

    # BDD sentence generation
    org_time = time.time()
    bdd_maker = Bdd_sentence_maker(id, columns)
    for row in entry:
        for col, val in zip(columns, row):
            bdd_maker.input_value(val, col)
    #print(f"Took {time.time() - org_time:.2f} seconds to generate BDD sentences for {name} with id {id}")
    org_time = time.time()
    # Prepare values for insertion
    main_rows = []
    for row in entry:
        data_dict = dict(zip(columns, row))
        sentence = bdd_maker.get_total_sentence(**data_dict)
        main_rows.append((id, name, *row, sentence))

    # Generate division cache
    division_cache = {
        key: generate_proportions(count)
        for key, count in bdd_maker.get_variable_counts().items()
    }

    # Dual and triple rows
    dual_rows = [(f"{key}={i}", prob) for key, probs in division_cache.items() for i, prob in enumerate(probs)]
    triple_rows = [(key, i, prob) for key, probs in division_cache.items() for i, prob in enumerate(probs)]
    # _dict string
    dict_update_str = ''.join(
        f"{key}={i}:{division[i]};"
        for key, division in division_cache.items()
        for i in range(len(division))
    )
    #print(f"Took {time.time() - org_time:.2f} seconds to prepare rows for {name} with id {id}")

    return main_rows, dual_rows, triple_rows, dict_update_str


def partition_rows(total_rows, num_people):
    base_rows = total_rows // num_people
    extra = total_rows % num_people

    distribution = [base_rows + 1 if i < extra else base_rows for i in range(num_people)]
    assert sum(distribution) == total_rows
    return distribution


def add_persons(table_name, amount_people: int, entries: list, columns: list):
    tables_each_person = partition_rows(entries, amount_people)
    all_main_rows = []
    all_dual_rows = []
    all_triple_rows = []
    all_dict_updates = []

    for x in range(amount_people):
        main, dual, triple, dict_str = insert_person_data(tables_each_person[x], columns)
        all_main_rows.extend(main)
        all_dual_rows.extend(dual)
        all_triple_rows.extend(triple)
        all_dict_updates.append(dict_str)
    org_time = time.time()
    combined_dict_update = ''.join(all_dict_updates)
    # Insert all at once
    with conn.cursor() as cur:
        #print(f"Inserting {len(all_main_rows)} total witness entries...")
        execute_values(cur,
            f"""INSERT INTO {table_name}
            (id, name, {', '.join(columns)}, _sentence)
            VALUES %s""",
            all_main_rows
        )

        #print(f"Inserting {len(all_dual_rows)} total dualrelation entries...")
        execute_values(cur,
            f"""INSERT INTO {table_name}_dualrelation (varval, prob)
            VALUES %s""",
            all_dual_rows
        )

        #print(f"Inserting {len(all_triple_rows)} total triplerelation entries...")
        execute_values(cur,
            f"""INSERT INTO {table_name}_triplerelation (var, val, prob)
            VALUES %s""",
            all_triple_rows
        )
        print(f"Inserting dictionary update of length {len(combined_dict_update)}...")
        #print("Updating dictionary...")
        try:
            query = f"""UPDATE _dict SET dict = add(dict, %s) WHERE name = %s""", (combined_dict_update, f"{table_name}_dict")
            cur.execute(
                f"""UPDATE _dict SET dict = add(dict, %s)
                    WHERE name = %s""",
                (combined_dict_update, f"{table_name}_dict")
            )
        except Exception as e:
            print(f"Error updating dictionary for {table_name}: {e}")
            print(f"Tried to update with: {combined_dict_update} of length {len(combined_dict_update)}")
            #Log the provided date for debugging
            with open("error_log.txt", "a") as f:
                f.write(f"Error updating dictionary for {table_name}: {e}\n")
                f.write(f"Tried to update with: {combined_dict_update} of length {len(combined_dict_update)}\n")
                f.write(f"QUERY: {query}\n")
            raise
    conn.commit()
    print(f"Done inserting {amount_people} persons into {table_name}, took {time.time() - org_time:.2f} seconds")


def create_table(table_name, columns, persons, rows, force_total_rows=True):
    import time
    start_time = time.time()
    #implement this for easy research
    prepare_database(table_name, columns)
    reset_names()  # Reset names to ensure fresh start
    tables_each_person = partition_rows(rows, persons)
    assert len(tables_each_person) == persons, f"Expected {persons} partitions, got {len(tables_each_person)}"
    add_persons(table_name, persons, rows, columns)
    print(f"Done creating table, took {time.time() - start_time:.2f} seconds")
    conn.commit()
    
# My naming conventions for (tablename):
# main table: tablename
# dictionary name: tablename_dict
# dual relation: tablename_dualrelation
# triple relation: tablename_triplerelation

def prepare_database(table_name, columns):
    """
    Drop and create the necessary tables for the given table name and columns. use naming conventions for dict and relations.
    """
    
    #First drop all
    execute_query(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    execute_query(f"DELETE FROM _dict WHERE name = '{table_name}_dict'")
    execute_query(f"INSERT INTO _dict VALUES ('{table_name}_dict', dictionary(''))")
    execute_query(f"DROP TABLE IF EXISTS {table_name}_dualrelation CASCADE")
    execute_query(f"DROP TABLE IF EXISTS {table_name}_triplerelation CASCADE")
    execute_query(f"CREATE TABLE {table_name} (id INTEGER, name TEXT, {', '.join([f'{col} TEXT' for col in columns])}, _sentence Bdd)")
    execute_query(f"CREATE TABLE {table_name}_dualrelation (varval TEXT, prob REAL)")
    execute_query(f"CREATE TABLE {table_name}_triplerelation (var TEXT, val INTEGER, prob REAL)")

def close_connection():
    """
    Close the database connection.
    """
    conn.commit()  # Commit any remaining changes
    cur.close()
    conn.close()
    print("Connection closed.")
