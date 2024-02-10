from input_function import*
import pandas as pd
import subprocess
import os

def generate_main_latex(template_path, output_path, data_dict):
    # Read the template
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        return

    # Replace placeholders with actual data
    for key, value in data_dict.items():
        placeholder = f'{{{{ {key} }}}}'  # Correct placeholder format
        template_content = template_content.replace(placeholder, str(value))
    # Write the output to a new file
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(template_content)
    except Exception as e:
        print(f"Error writing to output file: {e}")

def csv_to_latex_table(csv_path, latex_file_path, bool_old):
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Open a file to write the LaTeX code
    with open(latex_file_path, 'w', encoding='utf-8') as f:
        if bool_old is True:
            f.write("\\section*{Distances entre l'ancienne adresse et les officines voisines}\n")
        else:
            f.write("\\section*{Distances entre la nouvelle adresse et les officines voisines}\n")
        
        f.write("À la première ligne du tableau se trouvent les coordonnées de l'officine actuelle (avant déménagement) dont ce rapport fait objet.\n")
        # Start the table environment
        f.write('\\begin{table}[H]\n')
        f.write('\\centering\n')
        f.write('\\begin{tabular}{|r|l|l|c|}\n')
        f.write('\\hline\n')

        # Write the header row
        f.write('\\multicolumn{1}{|r|}{\\textbf{Numéro}} & \\textbf{Nom} & \\textbf{Adresse} & \\textbf{Distance} \\\\\n')
        f.write('\\hline\n')

        # Write the data rows
        for index, row in df.iterrows():
            if index == 0:
                continue
            f.write(f"{row[0]+1} & {row[2]} & \\begin{{tabular}}[c]{{@{{}}l@{{}}}}{row[3]}\\\\ {row[4]} {row[5]} \\end{{tabular}} & {round(row[10],2)} \\\\\n")
            f.write('\\hline\n')

        # End the table environment
        f.write('\\end{tabular}\n')
        f.write('\\caption{Toutes les distances sont mesurées par rapport à la pharmacie référencée à la première ligne du tableau et sont exprimées en mètres {[}m{]}}\n')
        f.write('\\end{table}\n')
        
def compile_tex_to_pdf(tex_folder, tex_filename):
    # Construct the full path to the TeX file and the output PDF file
    tex_path = os.path.join(tex_folder, tex_filename)

    # Check if the specified TeX file exists
    if os.path.exists(tex_path):
        # Compile the TeX file into a PDF
        command = f"pdflatex -output-directory {tex_folder} {tex_path}"
        subprocess.run(command, shell=True, check=True)
    else:
        print(f"The file {tex_path} does not exist.")