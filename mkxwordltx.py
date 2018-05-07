import csv
from pathlib import Path
from xwordgen_bh import Crossword


word_list_path = Path(__file__).parent / "words.csv"
output_path = Path(__file__).parent / "crossword.tex"
ltx_doc_start = \
"""% !TEX TS-program = pdflatex
\\documentclass[12pt]{article}

\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
\\usepackage[a4paper, margin=0.75in]{geometry}
\\usepackage{tabularx}
\\usepackage[table]{xcolor}

\\pagestyle{empty}

\\begin{document}
"""
ltx_doc_end = "\\end{document}\n"


def make_ltxtable():
    return "\\begin{table}[h!]\n" \
           "\\centering\\ttfamily\\tiny\n" \
           "\\setlength{\\tabcolsep}{2pt}\n" \
           "\\newlength{\\rowh}\n" \
           "\\setlength{\\rowh}{0.02\\textwidth}\n", \
           "\\end{table}\n"


def make_ltxtabularx(xword_grid):
    def xwordcell_to_ltxcell(cell):
        if cell == "-":
            return "\\cellcolor{black!25}"
        elif cell == "w":
            return "\\cellcolor{white}"
        else: return cell

    tabularx_init = "\\begin{tabularx}{1\\textwidth}{*{25}{|X}|}\n" \
                    "\\hline\n"
    rows = []
    # Split the xword grid into individual rows
    for xword_row in xword_grid.splitlines():
        # Split the xword row into cells, removing the empty ones at each end
        cells = xword_row.split(" ")[1:-1]
        # Convert xword cells into LaTeX cells
        cells = map(xwordcell_to_ltxcell, cells)
        # Join the LaTex cells together to make a LaTeX row data
        row_data = " & ".join(cells)
        # Create the full row and append to all_rows
        row = f"{row_data} \\tabularnewline[\\rowh] \\hline"
        rows.append(row)

    all_rows = "\n".join(rows)
    tabularx_end = "\n\\end{tabularx}\n"
    return f"{tabularx_init}{all_rows}{tabularx_end}"


def make_xword_ltxtable(xword_grid):
    ltxtable_init, ltxtable_end = make_ltxtable()
    ltxtabularx = make_ltxtabularx(xword_grid)
    return f"{ltxtable_init}{ltxtabularx}{ltxtable_end}"


if __name__ == '__main__':
    print("Loading word list from file...")
    word_list = []
    with word_list_path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word_list.append([row["word"], row["clue"]])

    time = 1
    print(f"Creating crossword... (takes {time} seconds)")
    xword = Crossword(25, 25, "-", 5000, word_list)
    xword.compute_crossword(time)
    xword_solution = xword.solution()
    xword_grid = xword.display()
    xword_legend = xword.legend()
    # print(xword.word_bank())
    # print(xword_solution)
    # print(xword_grid)
    # print(xword_legend)
    print(f"Used {len(xword.current_word_list)} out of {len(word_list)} words")
    print(f"Score: {xword.debug}")

    print("Making LaTeX table for crossword...")
    ltx_xword_table = make_xword_ltxtable(xword_grid)
    # TODO: make clues ltx
    print("Writing LaTeX document to crossword.tex...")
    with output_path.open(mode="w", encoding="utf-8") as f:
        f.write(ltx_doc_start)
        f.write(ltx_xword_table)
        f.write(ltx_doc_end)
        for solution_ln in xword_solution.splitlines(keepends=True):
            f.write(f"%  {solution_ln}")
    print("Finished making crossword.tex - run .\\make.py to compile!")
