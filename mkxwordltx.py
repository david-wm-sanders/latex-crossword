import csv
import itertools
import random
import uuid
from pathlib import Path
from xwordgen_bh import Crossword

_crossword_uuid = uuid.uuid4()

word_list_path = Path(__file__).parent / "words.csv"
output_path = Path(__file__).parent / f"{_crossword_uuid.hex}.tex"
ltx_doc_start = \
"""% !TEX TS-program = pdflatex
\\documentclass[12pt]{{article}}

\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{lmodern}}
\\usepackage[a4paper, margin=0.75in]{{geometry}}
\\usepackage{{tabularx}}
\\usepackage[table]{{xcolor}}
\\usepackage{{parskip}}
\\usepackage{{ragged2e}}
\\usepackage{{fancyhdr}}
\\usepackage[colorlinks=true, linkcolor=gray, citecolor=gray, urlcolor=gray]{{hyperref}}
\\usepackage{{latexsym}}

% Configure fancyhdr
\\renewcommand{{\\headrulewidth}}{{0.1mm}}
\\renewcommand{{\\footrulewidth}}{{0.1mm}}
\\renewcommand{{\\headrule}}{{
  \\vspace{{0.8mm}}\\vspace{{-\\baselineskip}}
  \\textcolor{{gray}}{{\\rule{{\\linewidth}}{{\\headrulewidth}}}}
}}
\\renewcommand{{\\footrule}}{{
  % \\vspace*{{0.8mm}}\\vspace*{{\\baselineskip}}
  \\textcolor{{gray}}{{\\rule{{\\linewidth}}{{\\footrulewidth}}}}
}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\lhead{{\\textcolor{{gray}}{{\\scriptsize {_crossword_uuid}}}}}
\\rhead{{\\textcolor{{gray}}{{\\scriptsize $\\Diamond$}}}}
\\lfoot{{\\textcolor{{gray}}{{\\scriptsize \\textit{{Generated with \\href{{https://github.com/david-wm-sanders/latex-crossword}}{{https://github.com/david-wm-sanders/latex-crossword}}}}}}}}
\\rfoot{{\\textcolor{{gray}}{{\\scriptsize \\thepage}}}}

\\begin{{document}}
""".format(_crossword_uuid=_crossword_uuid)
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
    def adjust_clue(clue):
        parts = clue.split(":")
        wordpos, cluetext = parts[0], parts[1].lstrip()
        wordpos_parts = wordpos.split(".")
        wordnum, pos = wordpos_parts[0], wordpos_parts[1].lstrip()
        pos_parts = pos.split(" ")
        wloc, wlen = pos_parts[0], pos_parts[2]
        return f"\\textbf{{{wordnum}.}} \\textit{{{wloc}({wlen}):}} {cluetext}"

    clues = ["\\pagebreak\n",
             # "\\newgeometry{margin=0.25in}\n",
             # "\\resetHeadWidth",
             # "\\pagestyle{fancy}\n",
             # "\\fancyhfoffset[E,O]{0pt}\n",
             "\\centering\n"]
    mpla = ["\\begin{minipage}[t]{0.43\\linewidth}\n",
            "\\vspace{0pt}\n",
            "{\\Centering\\underline{\\textsc{Across}}\\\\~\\\\}\n",
            "\\RaggedRight\n",
            "\\fontsize{10pt}{10pt}\\selectfont\n"]
    mprd = ["\\begin{minipage}[t]{0.43\\linewidth}\n",
            "\\vspace{0pt}\n",
            "{\\Centering\\underline{\\textsc{Down}}\\\\~\\\\}\n",
            "\\RaggedRight\n",
            "\\fontsize{10pt}{10pt}\\selectfont\n"]
    for clue in xword_legend.splitlines():
        position = clue.split(":")[0]
        if "across" in position:
            mpla.append(f"{adjust_clue(clue)}\\\\\n")
        elif "down" in position:
            adjust_clue(clue)
            mprd.append(f"{adjust_clue(clue)}\\\\\n")
        else:
            raise Exception(f"Bad clue position '{position}' not across or down!")

    mpla.append("\\end{minipage}")
    mprd.append("\\end{minipage}")

    parts = itertools.chain(clues, mpla,
                            ["\\hspace{4mm}\\textcolor{gray}{\\vline width 0.1mm}\\hspace{3mm}~\n"],
                            mprd, ["\\\\\n"])
    return "".join(parts)


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
    print(f"Writing LaTeX document to {output_path}...")
    with output_path.open(mode="w", encoding="utf-8") as f:
        f.write(ltx_doc_start)
        f.write(ltx_xword_table)
        f.write(ltx_xword_clues)
        f.write(ltx_doc_end)
        for solution_ln in xword_solution.splitlines(keepends=True):
            f.write(f"%  {solution_ln}")
    print(f"Finished making crossword - run .\\make.py {output_path.name} to compile!")
