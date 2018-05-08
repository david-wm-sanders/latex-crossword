import csv
import random
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
\\usepackage{parskip}

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
            return "\\cellcolor{black!10}"
        elif cell == "w":
            return "\\cellcolor{white}"
        else:
            return cell

    tabularx_init = "\\begin{tabularx}{1\\textwidth}{*{25}{|X}|}\n" \
                    "\\hline\n"
    rows = []
    # Split the xword grid into individual rows
    # Hack: Remove the last row that is unfilled due to a bug in xwordgen_bh
    xword_rows = xword_grid.splitlines()[0:-1]
    # print(len(xword_rows))
    for xword_row in xword_rows:
        # Split the xword row into cells, removing the empty string at the end
        # Hack, remove the last column - it is unfilled by xwordgen_bh
        cells = xword_row.split(" ")
        cells = cells[0:-2]
        # print(cells)
        # print(len(cells))
        # Convert xword cells into LaTeX cells
        cells = map(xwordcell_to_ltxcell, cells)
        # Join the LaTex cells together to make a LaTeX row data
        row_data = " & ".join(cells)
        # Create the full row and append to rows
        row = f"{row_data} \\tabularnewline[\\rowh] \\hline"
        rows.append(row)

    all_rows = "\n".join(rows)
    tabularx_end = "\n\\end{tabularx}\n"
    return f"{tabularx_init}{all_rows}{tabularx_end}"


def make_xword_ltxtable(xword_grid):
    ltxtable_init, ltxtable_end = make_ltxtable()
    ltxtabularx = make_ltxtabularx(xword_grid)
    return f"{ltxtable_init}{ltxtabularx}{ltxtable_end}"


def make_xword_clues(xword_legend):
    clues = ["\\pagebreak\n",
             "\\fontsize{10pt}{10pt}\\selectfont\n"]
    for clue in xword_legend.splitlines():
        clues.append(f"{clue}\\\\\n")
    return "".join(clues)


def filter_word_randomly(word):
    return random.choice([True, True, False])


if __name__ == '__main__':
    print("Loading word list from file...")
    word_list = []
    with word_list_path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word_list.append([row["word"], row["clue"]])
    # Remove some words from the long word list at random
    # This increases our chance of getting more shorter words in the crossword
    word_list = list(filter(filter_word_randomly, word_list))

    time = 30
    print(f"Creating crossword... (takes {time} seconds)")
    xword = Crossword(26, 26, "-", 5000, word_list)
    xword.compute_crossword(time, spins=3)
    xword_solution = xword.solution()
    xword_grid = xword.display()
    xword_legend = xword.legend()
    print(f"Used {len(xword.current_word_list)} out of {len(word_list)} words")
    print(f"Cycles: {xword.debug}")
    print(xword_solution)

    print("Making LaTeX table for crossword...")
    ltx_xword_table = make_xword_ltxtable(xword_grid)
    ltx_xword_clues = make_xword_clues(xword_legend)
    print("Writing LaTeX document to crossword.tex...")
    with output_path.open(mode="w", encoding="utf-8") as f:
        f.write(ltx_doc_start)
        f.write(ltx_xword_table)
        f.write(ltx_xword_clues)
        f.write(ltx_doc_end)
        for solution_ln in xword_solution.splitlines(keepends=True):
            f.write(f"%  {solution_ln}")
    print("Finished making crossword.tex - run .\\make.py to compile!")
