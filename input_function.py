import geopandas as gpd
from shapely.geometry import Point

def get_coord_by_pharma_id(gdf):
    while True:
            id_number = input("Numéro d'identification de la pharmacie : ")
            # Filter the GeoDataFrame for the given id_number
            matching_row = gdf[gdf["Numéro d'autorisation"] == id_number]
            
            # Check if there is a matching row
            if not matching_row.empty:
                # Return the geometry
                return matching_row.iloc[0]['geometry']
            else:
                # Return None or an appropriate response if no match is found
                print("Lolilol, mauvais numéro d'identification")


def coordinate_new_implantation():
    while True:
        try:
            # Prompt the user for input
            user_input = input("Coordonnées X-Y de la nouvelle implentation : ")

            # Split the input string into a list at the comma and convert each item to an integer
            input_list = [float(element.strip()) for element in user_input.split(',')]

            # Check if exactly two integers were provided
            if len(input_list) == 2:
                return Point(input_list)
            else:
                print("Uniquement les coordonnées X-Y sont nécessaires, donc 2 valeurs")
        except ValueError:
            print("ptdr tu sais pas écrire une coordonnées comme tout le monde ?")

def adress_new_implantation():
    while True:
        # Prompt the user for input
        user_input = input("Adresse de la nouvelle implentation avec le format suivant: 'Adresse, Code Postal, Ville' : ")

        # Split the input string into a list at the comma
        input_list = [element.strip() for element in user_input.split(',')]

        # Check if exactly three components were provided
        if len(input_list) == 3:
            return input_list
        else:
            print("Faut lire la demande... 'Adresse, Code Postal, Ville' séparé par une virgule")

def date_and_ref():
    while True:
        try:
            # Prompt the user for input
            user_input = input("Date (si différente d'aujourd'hui) et reférérence du dossier (légende du plan) dans le format suivant 'DD/MM/YYYY, 24.XXX' : ")

            # Split the input string into a list at the comma and convert each item to an integer
            input_list = [element.strip() for element in user_input.split(',')]

            # Check if exactly two integers were provided
            if len(input_list) == 2:
                if len(input_list[0]) == 10:
                    return input_list
                else:
                    input_list[0] = '\\today'
                    return input_list
            else:
                print("Faut lire la demande... 'DD/MM/YYYY, 24.XXX' séparé par une virgule")
        except ValueError:
            print("Nique toi, je sais pas comment c'est possible d'avoir cette erreur")

def project_type():
    while True:
        try: 
            print("Sélectionner le type de rapport à générer :")
            print("1) Transfert")
            print("2) Fusion")
            print("3) Transfert + fusion")
            userInput = int(input("Choisir le numéro correspondant : "))

            if userInput not in {1, 2, 3}:
                print("\nwesh tu essaye de faire quoi\n")
            else:
                if userInput == 3:
                    return userInput
                else:
                    print("\nC'est pas encore implémenté mdrrrr sois patient bebou\n")   
        except ValueError:
            print("heuuuuuuu appelle moi mdr")
