from input_function import*
import pandas as pd
import subprocess
import os
from pathlib import Path

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

def csv_to_latex_table(csv_path, latex_file_path, bool_old, id_old_pharmacy):
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Open a file to write the LaTeX code
    with open(latex_file_path, 'w', encoding='utf-8') as f:
        if bool_old is True:
            f.write("\\section*{Distances entre l'ancienne adresse et les officines voisines}\n")
        else:
            f.write("\\section*{Distances entre la nouvelle adresse et les officines voisines}\n")
        
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
            if row[1] == id_old_pharmacy:
                continue
            f.write(f"{row[0]} & {row[2]} & \\begin{{tabular}}[c]{{@{{}}l@{{}}}}{row[3]}\\\\ {row[4]} {row[5]} \\end{{tabular}} & {round(row[10],2)} \\\\\n")
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

def list_of_people(folder_path, FOLDER_NAME_TEX, HABITANTS_TEX):
    folder = Path(folder_path)
    file = next(folder.glob("*_filled.csv"), None)

    if file:
        df = pd.read_csv(file)
        df_summary = df.groupby(['CODEPOSTAL','ZONE_ADRES','RUE_NOM'])['NBR_HABITANTS'].sum().reset_index()
        df_summary.to_csv(folder_path + "/people_by_street.csv", index=False)
        bool_csv_filled = True
        latex_file_path = os.path.join(folder_path, FOLDER_NAME_TEX, HABITANTS_TEX)
        habitants_to_table(df, latex_file_path, bool_csv_filled)
        return bool_csv_filled
    else:
        bool_csv_filled = False
        latex_file_path = os.path.join(folder_path, FOLDER_NAME_TEX, HABITANTS_TEX)
        habitants_to_table(None, latex_file_path, bool_csv_filled)
        return bool_csv_filled

def habitants_to_table(df, latex_file_path, bool_csv_filled):
    # Open a file to write the LaTeX code
    with open(latex_file_path, 'w', encoding='utf-8') as f:

        f.write("\\section*{Distances entre la nouvelle adresse et les officines voisines}\n")
        
        # Start the table environment
        f.write('\\begin{table}[H]\n')
        f.write('\\centering\n')
        f.write('\\begin{tabular}{|r|l|l|c|}\n')
        f.write('\\hline\n')

        # Write the header row
        f.write('\\multicolumn{1}{|r|}{\\textbf{Rue}} & \\textbf{Ville} & \\textbf{Code Postal} & \\textbf{Habitants} \\\\\n')
        f.write('\\hline\n')

        if bool_csv_filled:
            # Write the data rows
            for index, row in df.iterrows():
                if index == 0:
                    continue
                f.write(f"{row[2]} & {row[1]} & {row[0]} & {row[3]} \\\\\n")
                f.write('\\hline\n')
        else:
            f.write(f"Rue du Lorem & Ipsum & 1.6180 & 3.1415 \\\\\n")
            f.write('\\hline\n')

                # End the table environment
        f.write('\\end{tabular}\n')
        f.write("\\caption{Nombre d'habitants par rue dans la Zone d'Influence Géographique}\n")
        f.write('\\end{table}\n')