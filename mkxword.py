from pathlib import Path

output_path = Path(__file__).parent / "output.tex"

ltx_doc_start = \
"""% !TEX TS-program = pdflatex
\\documentclass[12pt]{article}

\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
\\usepackage[a4paper, margin=0.75in]{geometry}
\\usepackage{tabularx}

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


with output_path.open(mode="w", encoding="utf-8") as f:
    f.write(ltx_doc_start)
    ltx_xword_table = make_xword_ltxtable()
    f.write(ltx_xword_table)
    f.write(ltx_doc_end)
