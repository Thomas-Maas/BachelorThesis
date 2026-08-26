import matplotlib.pyplot as plt
import json
from typing import List, Tuple, Union
from statsmodels.nonparametric.smoothers_lowess import lowess


def parse_log_file(file_path: str):
    with open(file_path, "r") as f:
        raw = f.read()

    blocks = [b.strip() for b in raw.split("------------------------------------------------------------") if b.strip()]
    parsed = []
    for block in blocks:
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError:
            break
    return parsed

def plot_single_subplot(ax, data, label, x_key, y_keys, show_dict_vars=False, log_x=False, use_trendline=False):

    if isinstance(x_key, tuple):
        x_vals = [tuple(entry[k] for k in x_key) for entry in data]
        x_label = " × ".join(x_key)
    else:
        x_vals = [entry[x_key] for entry in data]
        x_label = x_key

        for y_key in y_keys:
            alphaval = 0.15 if use_trendline else 1
            y_vals = [entry[y_key] for entry in data]
            ax.plot(x_vals, y_vals, marker='o', linestyle='', label=y_key, alpha=alphaval)

            if use_trendline:
                try:
                    # LOWESS smoothing
                    smoothed = lowess(y_vals, x_vals, frac=0.15, return_sorted=True)
                    ax.plot(smoothed[:, 0], smoothed[:, 1], label=f"{y_key} (trend)", linewidth=2)
                except Exception as e:
                    print(f"Trendline error for {y_key}: {e}")


    ax.set_xlabel(x_label)
    ax.set_ylabel("Execution Time (ms)")
    title = f"{label} — Execution Time vs {x_label}"
    if show_dict_vars and data:
        title += f"\n#vars: {data[0].get('dict_vars')} | #values: {data[0].get('dict_values')}"
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    ax.tick_params(axis='x', rotation=45)

    # Apply log scale if requested
    if log_x:
        if all(isinstance(x, (int, float)) and x > 0 for x in x_vals):
            ax.set_xscale('log')


def plot_subplots_in_one_window(
    datasets: List[Tuple[str, List[dict]]],
    x_key: Union[str, Tuple[str]],
    y_keys: List[str],
    show_dict_vars=False,
    log_x=False,
    use_trendline=False
):

    n = len(datasets)
    if n <= 2:
        cols = n
        rows = 1
    else:
        cols = 2
        rows = (n + 1) // 2  # round up


    # Adjust size: width per column, height per row
    fig, axs = plt.subplots(rows, cols, figsize=(6 * cols, 4.5 * rows), squeeze=False, sharex=False, sharey=False)

    for idx, (label, data) in enumerate(datasets):
        r, c = divmod(idx, cols)
        plot_single_subplot(axs[r][c], data, label, x_key, y_keys, show_dict_vars, log_x, use_trendline)
    

    # Hide any unused subplots (if datasets % grid != 0)
    for i in range(n, rows * cols):
        r, c = divmod(i, cols)
        fig.delaxes(axs[r][c])

    plt.tight_layout(pad=2.0)
    plt.show()

# Example usage
if __name__ == "__main__":
    test1 = "1_person_increasing_entries_max_4000.log"
    test2 = "5_person_increasing_entries_max_4000.log"
    test3 = "10_person_increasing_entries_max_4000.log"
    test4 = "20_person_increasing_entries_max_4000.log"

    logs = [
        ("5 dict vars", parse_log_file(test1)),
        ("25 dict vars", parse_log_file(test2)),
        ("50 dict vars", parse_log_file(test3)),
        ("100 dict vars", parse_log_file(test4)),
        
    ]

    plot_subplots_in_one_window(
        logs,
        "total_table_rows",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True
    )
    
    ptest1 = "500_all_persons.log"
    ptest2 = "2000_rows_2000_persons.log"
    ptest3 = "1000_all_persons.log"
    ptest4 = "2000_rows_increasing_persons_max_2000.log"
    log = parse_log_file(ptest1)
    log2 = parse_log_file(ptest2)
    log3 = parse_log_file(ptest3)
    log4 = parse_log_file(ptest4)
    logs = [
        ("1000 rows", log3),
        
    ]
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True
    )
    
    ctest1 = "1_25_columns_50_200.log"
    
    log1 = parse_log_file(ctest1)
    logs = [
        ("Amount of columns increasing", log1),
    ]
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True
    )

    ftest1 = "inc_dict_vars_1.log"
    ftest2 = "inc_dict_vars_2.log"
    ftest3 = "inc_dict_vars_max_people_only_double_rows.log"
    ftest4 = "inc_dict_vars_max_people_only.log"
    log1 = parse_log_file(ftest1)
    log2 = parse_log_file(ftest2)
    log3 = parse_log_file(ftest3)
    log4 = parse_log_file(ftest4)
    logs = [
        #("inc_dict_vars_1", log1),
        #("inc_dict_vars_2", log2),
        ("3000 rows", log4),
        ("6000 rows", log3),
        
    ]
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True, log_x=True
    )
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True
    )
    
    mest1 = "mega_3_col.log"
    mest2 = "mega_4_col.log"
    #mest3 = "mega_5_col.log"
    #mest4 = "mega_6_col.log"
    log1 = parse_log_file(mest1)
    log2 = parse_log_file(mest2)
    logs = [
        ("20000 rows", log1),
        #("mega_4_col", log2),
    ]
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True, log_x=True
    )
    
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True
    )
    log1 = parse_log_file("mega_col_inc_1000_rows.log")
    logs = [
        ("Increase in dict vars by adding columns. Id density of 10, 1000 rows", log1),
    ]
    
    plot_subplots_in_one_window(
        logs,
        "dict_vars",
        ["base_execution_time", "dual_execution_time", "triple_execution_time"],
        show_dict_vars=False, use_trendline=True
    )