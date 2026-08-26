# Reimagining Probability Storage and Variable Assignments in DuBio

**A Comparative Study of Data Structures**
Thomas Maas, University of Twente — TScIT 43, July 2025

Full paper: [Full_Paper_Thomas_Maas.pdf](Full_Paper_Thomas_Maas.pdf)

## Abstract

Probabilistic databases treat uncertain data as a valuable asset rather than a flaw, using intrinsic probabilities to draw conclusions from merged or conflicting data. This project investigates a bottleneck in **DuBio**, a PostgreSQL extension for probabilistic data developed at the University of Twente: DuBio stores random variables and their probabilities in a single dictionary per row, which is expected to become a performance bottleneck as the number of variables grows.

This research implements and benchmarks two alternative variable-storage structures — a **tuple table** (`'A=1', 0.5`) and a **triplet table** (`'A', 1, 0.5`) — and an accompanying PostgreSQL-only algorithm for computing the probability of conjunctive sentences (e.g. `X=0 AND Y=1 AND Z=2`). Execution time is compared against DuBio's native dictionary + Binary Decision Diagram (BDD) approach across varying numbers of rows, columns, and dictionary variables.

**Key finding:** the tuple and triplet methods scale far better than DuBio's dictionary lookup as the number of variables grows, and only underperform DuBio on very small datasets (fewer than ~50 variables).

## Repository contents

- **`synthetic_data_generator*.py`** — generates synthetic datasets (people with randomized properties such as hair color and length) with configurable rows, columns, and IDs, and populates a DuBio dictionary, a tuple table, and a triplet table with matching data and sentences. Several variants exist reflecting iterative performance optimization (`_faster`, `_faster_even_faster`).
- **`database_interaction.py`** — helper functions for running SQL queries against the database and capturing `EXPLAIN ANALYZE` execution plans.
- **`prob_calculator.py`** — implements the tuple/triplet probability-resolution algorithm described in the paper (Algorithm 1 / Appendix A) and runs it against generated sentences.
- **`performance_analysis.py`** (and older working copies) — orchestrates benchmark runs across varying dataset parameters (rows, columns, variables/ID density) and logs execution times.
- **`graph_from_log.py` / `graph_from_log2.py`** — parse the JSON-formatted `.log` files produced by the benchmark runs and plot execution-time comparisons (DuBio vs. tuple vs. triplet), saved to `Saved_Figures/`.
- **`bdd_traversal.py`** — small standalone example of constructing and rendering a Binary Decision Diagram with `pyeda`/`graphviz`, illustrating how DuBio resolves sentences internally.
- **`random_values.py`** — utilities for generating randomized synthetic property values (names, car attributes, etc.) used by the data generators.
- **`*.log`** — raw benchmark output (execution times per query type, varying rows/columns/persons) used to produce the figures in the paper.

## Setup

1. Install dependencies:
   ```
   pip install psycopg2-binary python-dotenv matplotlib statsmodels numpy pyeda graphviz
   ```
2. Copy `.env.example` to `.env` and fill in your PostgreSQL/DuBio database credentials:
   ```
   cp .env.example .env
   ```
3. Run a script, e.g.:
   ```
   python synthetic_data_generator.py
   python performance_analysis.py
   ```

Note: DuBio must be installed on the target PostgreSQL instance to generate and query its dictionary structures; the tuple/triplet methods only require standard PostgreSQL.
