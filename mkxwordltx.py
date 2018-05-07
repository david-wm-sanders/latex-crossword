from pathlib import Path
from xwordgen_bh import Crossword


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
ltx_doc_end = "\\end{document}"


def make_ltxtable():
    return "\\begin{table}[h!]\n" \
           "\\centering\\ttfamily\\tiny\n" \
           "\\setlength{\\tabcolsep}{2pt}\n" \
           "\\newlength{\\rowh}\n" \
           "\\setlength{\\rowh}{0.02\\textwidth}\n", \
           "\\end{table}\n"


def make_ltxtabularx():
    tabularx_init = "\\begin{tabularx}{1\\textwidth}{*{25}{|X}|}\n" \
                    "\\hline\n"
    rows = []
    for i in range(25):
        row = "x & x & x & x & x & " \
              "x & x & x & x & x & " \
              "x & x & x & x & x & " \
              "x & x & x & x & x & " \
              "x & x & x & x & x \\tabularnewline[\\rowh] \\hline"
        rows.append(row)
    tabularx_rows = "\n".join(rows)
    tabularx_end = "\n\\end{tabularx}\n"
    return f"{tabularx_init}{tabularx_rows}{tabularx_end}"


def make_xword_ltxtable():
    ltxtable_init, ltxtable_end = make_ltxtable()
    ltxtabularx = make_ltxtabularx()
    return f"{ltxtable_init}{ltxtabularx}{ltxtable_end}"


if __name__ == '__main__':
    print("Loading word list from file...")
    word_list = []
    # TODO: load wordlist from CSV file
    time = 5
    print(f"Creating crossword... (taking {time} seconds)")
    xword = Crossword(25, 25, "-", 5000, word_list)
    xword.compute_crossword(time)

    print(xword.display())
    print(xword.solution())
    print(xword.legend())
    print(len(xword.current_word_list), 'out of', len(word_list))
    print(xword.debug)

    ltx_xword_table = make_xword_ltxtable()
    with output_path.open(mode="w", encoding="utf-8") as f:
        f.write(ltx_doc_start)
        f.write(ltx_xword_table)
        f.write(ltx_doc_end)
