import os
import psycopg2
import random
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"]
)

class person_type(Enum):
    WITNESS = 1
    SUSPECT = 2

import random

def generate_proportions(number):
    if number < 1:
        raise ValueError("Number must be >= 1")
    if number == 1:
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

    return rounded






class Bdd_sentence_maker:
    def __init__(self, id: str, prefix: str):
        self.id = id
        self.color_values = list()
        self.car_values = list()
        self.time_values = list()
        self.bogus1_values = list()
        self.bogus2_values = list()
        self.bogus3_values = list()
        self.bogus4_values = list()
        self.variable_counts = dict()
        self.prefix = prefix  # 'w' for witness, 's' for suspect
    
    def input_color_value(self, color: str):
        """
        Adds a color value to the color_values list if it does not already exist.
        """
        if color not in self.color_values:
            self.color_values.append(color)
    def input_car_value(self, car: str):
        """
        Adds a car value to the car_values list if it does not already exist.
        """
        if car not in self.car_values:
            self.car_values.append(car)
    def input_time_value(self, time: str):
        """
        Adds a time value to the time_values list if it does not already exist.
        """
        if time not in self.time_values:
            self.time_values.append(time)
    def input_bogus1_value(self, bogus1: str):
        """
        Adds a bogus1 value to the bogus1_values list if it does not already exist.
        """
        if bogus1 not in self.bogus1_values:
            self.bogus1_values.append(bogus1)
    def input_bogus2_value(self, bogus2: str):
        """
        Adds a bogus2 value to the bogus2_values list if it does not already exist.
        """
        if bogus2 not in self.bogus2_values:
            self.bogus2_values.append(bogus2)
    def input_bogus3_value(self, bogus3: str):
        """
        Adds a bogus3 value to the bogus3_values list if it does not already exist.
        """
        if bogus3 not in self.bogus3_values:
            self.bogus3_values.append(bogus3)
    def input_bogus4_value(self, bogus4: str):
        """
        Adds a bogus4 value to the bogus4_values list if it does not already exist.
        """
        if bogus4 not in self.bogus4_values:
            self.bogus4_values.append(bogus4)

    def get_color_sentence(self, color: str) -> str:
        """
        Returns a BDD sentence for the given color.
        """
        variable = f"{self.prefix}a{self.id}"
        color_value = self.color_values.index(color)
        if len(self.color_values) <= 1:
            return "1"  # If there's only one time, we can assume it's true
        return f"{variable}={color_value}"
    
    def get_car_sentence(self, car: str) -> str:
        """
        Returns a BDD sentence for the given car.
        """
        variable = f"{self.prefix}b{self.id}"
        car_value = self.car_values.index(car)
        if len(self.car_values) <= 1:
            return "1"  # If there's only one time, we can assume it's true
        return f"{variable}={car_value}"
    
    def get_time_sentence(self, time: str) -> str:
        """
        Returns a BDD sentence for the given time.
        """
        variable = f"{self.prefix}c{self.id}"
        time_value = self.time_values.index(time)
        if len(self.time_values) <= 1:
            return "1"  # If there's only one time, we can assume it's true
        return f"{variable}={time_value}"
    
    def get_bogus1_sentence(self, bogus1: str) -> str:
        """
        Returns a BDD sentence for the given bogus1 value.
        """
        variable = f"{self.prefix}d1{self.id}"
        bogus1_value = self.bogus1_values.index(bogus1)
        if len(self.bogus1_values) <= 1:
            return "1"
        return f"{variable}={bogus1_value}"
    def get_bogus2_sentence(self, bogus2: str) -> str:
        """
        Returns a BDD sentence for the given bogus2 value.
        """
        variable = f"{self.prefix}d2{self.id}"
        bogus2_value = self.bogus2_values.index(bogus2)
        if len(self.bogus2_values) <= 1:
            return "1"
        return f"{variable}={bogus2_value}"
    def get_bogus3_sentence(self, bogus3: str) -> str:
        """
        Returns a BDD sentence for the given bogus3 value.
        """
        variable = f"{self.prefix}d3{self.id}"
        bogus3_value = self.bogus3_values.index(bogus3)
        if len(self.bogus3_values) <= 1:
            return "1"
        return f"{variable}={bogus3_value}"
    def get_bogus4_sentence(self, bogus4: str) -> str:
        """
        Returns a BDD sentence for the given bogus4 value.
        """
        variable = f"{self.prefix}d4{self.id}"
        bogus4_value = self.bogus4_values.index(bogus4)
        if len(self.bogus4_values) <= 1:
            return "1"
        return f"{variable}={bogus4_value}"
    
    def get_total_sentence(self, color: str, car: str, time: str, bogus1: str, bogus2: str, bogus3: str, bogus4: str) -> str:
        """
        Returns a BDD sentence for the given color, car, and time.
        """
        color_sentence = self.get_color_sentence(color)
        car_sentence = self.get_car_sentence(car)
        time_sentence = self.get_time_sentence(time)
        bogus1_sentence = self.get_bogus1_sentence(bogus1)
        bogus2_sentence = self.get_bogus2_sentence(bogus2)
        bogus3_sentence = self.get_bogus3_sentence(bogus3)
        bogus4_sentence = self.get_bogus4_sentence(bogus4)
        print(f"Getting total sentence for color: {color}, car: {car}, time: {time}, bogus1: {bogus1}, bogus2: {bogus2}, bogus3: {bogus3}, bogus4: {bogus4}, id: {self.id}, prefix: {self.prefix}")
        return f"{color_sentence}&{car_sentence}&{time_sentence}&{bogus1_sentence}&{bogus2_sentence}&{bogus3_sentence}&{bogus4_sentence}"
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
        self.variable_counts[f"{self.prefix}a{self.id}"] = len(self.color_values)
        self.variable_counts[f"{self.prefix}b{self.id}"] = len(self.car_values)
        self.variable_counts[f"{self.prefix}c{self.id}"] = len(self.time_values)
        self.variable_counts[f"{self.prefix}d1{self.id}"] = len(self.bogus1_values)
        self.variable_counts[f"{self.prefix}d2{self.id}"] = len(self.bogus2_values)
        self.variable_counts[f"{self.prefix}d3{self.id}"] = len(self.bogus3_values)
        self.variable_counts[f"{self.prefix}d4{self.id}"] = len(self.bogus4_values)
        print(f"Variable counts for id: {self.id}, prefix: {self.prefix}: {self.variable_counts}")
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


execute_query("DELETE FROM _dict WHERE name = 'thomasdict'")
execute_query("INSERT INTO _dict VALUES ('thomasdict', dictionary(''))")
execute_query_print("SELECT print(dict) FROM _dict WHERE name = 'thomasdict'")
execute_query("DROP TABLE IF EXISTS triplerelation CASCADE")
execute_query("CREATE TABLE triplerelation (var TEXT, val INTEGER, prob REAL)")
execute_query("DROP TABLE IF EXISTS dualrelation CASCADE")
execute_query("CREATE TABLE dualrelation (varval TEXT, prob REAL)")
execute_query("DROP TABLE IF EXISTS t_witnesses CASCADE")
execute_query("CREATE TABLE t_witnesses (id INTEGER, name TEXT, color TEXT, car TEXT, time TEXT, bogus1 TEXT, bogus2 TEXT, bogus3 TEXT, bogus4 TEXT, _sentence Bdd)")
execute_query("DROP TABLE IF EXISTS t_suspects")
execute_query("CREATE TABLE t_suspects (id INTEGER, name TEXT, color TEXT, car TEXT, time TEXT, bogus1 TEXT, bogus2 TEXT, bogus3 TEXT, bogus4 TEXT, _sentence Bdd)")
execute_query("DROP TABLE IF EXISTS t_trustworthiness")
execute_query("CREATE TABLE t_trustworthiness (id INTEGER, name TEXT, _sentence Bdd)")

def insert_person(entry_count: int, person_type: person_type):
    """
    Insert a witness with the given name and random attributes into the t_witnesses table.
    """
    from random_values import get_available_witness_id_name, get_available_suspect_id_name, get_random_car_color, get_random_car_type, get_random_time_of_day, get_random_bogus
    id, name = None, None
    if person_type == person_type.WITNESS:
        id, name = get_available_witness_id_name()
    elif person_type == person_type.SUSPECT:
        id, name = get_available_suspect_id_name()
    else:
        raise ValueError("Invalid person type. Use person_type.WITNESS or person_type.SUSPECT.")
    entry = []
    bdd_makers = dict()
    for x in range(entry_count):
        color = get_random_car_color()
        car = get_random_car_type()
        time = get_random_time_of_day()
        bogus1 = get_random_bogus()
        bogus2 = get_random_bogus()
        bogus3 = get_random_bogus()
        bogus4 = get_random_bogus()
        entry.append((id, name, color, car, time, bogus1, bogus2, bogus3, bogus4))
        if person_type == person_type.WITNESS:
            bdd_makers[id] = Bdd_sentence_maker(id, 'w')
        elif person_type == person_type.SUSPECT:
            bdd_makers[id] = Bdd_sentence_maker(id, 's')  # 'w' for witness
    entry = list(set(entry))  # Remove duplicates
    sentence_occurrences = dict()
    for person in entry:
        bdd_makers[person[0]].input_color_value(person[2])
        bdd_makers[person[0]].input_car_value(person[3])
        bdd_makers[person[0]].input_time_value(person[4])
        bdd_makers[person[0]].input_bogus1_value(person[5])
        bdd_makers[person[0]].input_bogus2_value(person[6])
        bdd_makers[person[0]].input_bogus3_value(person[7])
        bdd_makers[person[0]].input_bogus4_value(person[8])
        
    # Now we can generate the sentence for each person
    for person in entry:
        sentence = bdd_makers[person[0]].get_total_sentence(person[2], person[3], person[4], person[5], person[6], person[7], person[8])
        sentence_occurrences = bdd_makers[person[0]].get_variable_counts()
        print(f"Person: {person}, Sentence: {sentence}, Occurrences: {sentence_occurrences}")
        cur.execute(f"INSERT INTO t_{'witnesses' if person_type == person_type.WITNESS else 'suspects'} (id, name, color, car, time, bogus1, bogus2, bogus3, bogus4, _sentence) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, Bdd('{sentence}'))", (person[0], person[1], person[2], person[3], person[4], person[5], person[6], person[7], person[8]))
    
    #Now add this to the dictionary
    #TODO change this so that we first formulate a proper sentence then immediately add it
    #print(sentence_occurrences)
    
    for i, (key, value) in enumerate(sentence_occurrences.items()):
        division = generate_proportions(value)
        formulated_sentence = ''.join([f"{key}={j}:{division[j]};" for j in range(value)])
        cur.execute(f"UPDATE _dict SET dict=add(dict, '{formulated_sentence}') WHERE name='thomasdict'")
        #print(f"Appending value {formulated_sentence} to the dictionary")
        #cur.execute("INSERT INTO triplerelation (var, value, prob) VALUES (%s, %s, %s)", (key, j, division[j]))
    for i, (key, value) in enumerate(sentence_occurrences.items()):
        division = generate_proportions(value)
        for j in range(value):
            varvalue = f"{key}={j}"
            cur.execute("INSERT INTO dualrelation (varval, prob) VALUES (%s, %s)", (varvalue, division[j]))
            #print(f"Appending value {formulated_sentence} to the dual relation")
    for i, (key, value) in enumerate(sentence_occurrences.items()):
        division = generate_proportions(value)
        for j in range(value):
            cur.execute("INSERT INTO triplerelation (var, val, prob) VALUES (%s, %s, %s)", (key, j, division[j]))
            #print(f"Appending value {varvalue} to the triplerelation table")    
    
    #Add this to var, value, prob table
    #Add this to varvalue, prob table
    #Also add them to the t_trustworthiness table
    if person_type == person_type.WITNESS:
        
        added_to_trustworthiness = set()
        for witness in entry:
            id, name = witness[0], witness[1]
            if id not in added_to_trustworthiness:
                
                added_to_trustworthiness.add(id)
                #now also insert the witness into the t_trustworthiness table
                cur.execute("INSERT INTO t_trustworthiness (id, name, _sentence) VALUES (%s, %s, Bdd('1'))", (id, name))


def add_persons(amount_people, min_entries, max_entries, person_type: person_type):
    """
    Add a number of persons (witnesses or suspects) with random attributes to the respective table.
    """
    
    if person_type == person_type.WITNESS:
        for _ in range(amount_people):
            entry_count = random.randint(min_entries, max_entries)
            insert_person(entry_count, person_type.WITNESS)
    elif person_type == person_type.SUSPECT:
        for _ in range(amount_people):
            entry_count = random.randint(min_entries, max_entries)
            insert_person(entry_count, person_type.SUSPECT)
    else:
        raise ValueError("Invalid person type. Use person_type.WITNESS or person_type.SUSPECT.")


def create_witness_table(persons, min_entries, max_entries):
    """
    Create a witness table with the specified number of persons and random attributes.
    """
    add_persons(persons, min_entries, max_entries, person_type.WITNESS)
    conn.commit()
    cur.close()
    conn.close()

def create_suspect_table(persons, min_entries, max_entries):
    """
    Create a suspect table with the specified number of persons and random attributes.
    """
    add_persons(persons, min_entries, max_entries, person_type.SUSPECT)
    conn.commit()
    cur.close()
    conn.close()



