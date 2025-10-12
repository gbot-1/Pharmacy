import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from distance_function import get_planar_distance

def get_coord_by_pharma_id(gdf):
    while True:
            id_number = input("Numéro d'identification de la pharmacie : ")
            # Filter the GeoDataFrame for the given id_number
            matching_row = gdf[gdf["Numéro d'autorisation"] == id_number]
            
            # Check if there is a matching row
            if not matching_row.empty:
                # Return the geometry
                return matching_row.iloc[0]['geometry'], int(id_number)
            else:
                # Return None or an appropriate response if no match is found
                print("Lolilol, mauvais numéro d'identification")


def coordinate_new_implantation():
    while True:
        try:
            # Prompt the user for input
            user_input = input("Coordonnées X-Y (Lambert 2008) de la nouvelle implentation : ")

            # Split the input string into a list at the comma and convert each item to an integer
            input_list = [float(element.strip()) for element in user_input.split(',')]

            # Check if exactly two integers were provided
            if len(input_list) == 2:
                x, y = input_list
                if x > 520000 and x < 796000:
                    if y > 520000 and y < 745000:
                       return Point(input_list)
                    else:
                        print("Y-coord hors limite")
                else:
                    print("X-coord hors limite")
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
            print("1) Transfert simple")
            print("2) Transfert + Fusion")
            print("3) Fusion")
            userInput = int(input("Choisir le numéro correspondant : "))

            if userInput not in {1, 2, 3}:
                print("\nwesh tu essaye de faire quoi\n")
            else:
                return userInput
        except ValueError:
            print("heuuuuuuu appelle moi mdr")

def selection_pharmacies(gdf_init, geometry, nb_point, new_coordinates): 
    while True:
        closest_points = get_planar_distance(gdf_init, geometry, nb_point)

        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot the points
        closest_points.plot(ax=ax, marker='o', color='red', markersize=50)

        # Add labels (row indices) next to each point
        for idx, row in closest_points.iterrows():
            # Get the coordinates
            x, y = row.geometry.x, row.geometry.y
            
            # Add text label with slight offset
            ax.annotate(str(idx), (x, y), xytext=(5, 5), 
                        textcoords='offset points', fontsize=10)
            
        plt.scatter(new_coordinates.x, new_coordinates.y, marker='o', color='blue')

        plt.show()

        print("Sélection des pharmacies :")
        print("Pour augmenter la sélection, taper 99")
        print("Pour annuler, taper -1")
        user_input = input("Pharmacies choisies, séparées par une virgule : ")

        input_list = [int(element.strip()) for element in user_input.split(',')]

        if input_list[0] == 99:
            nb_point += 5
        elif input_list[0] == -1:
            exit()
        else:
            input_list.insert(0,0)
            input_list.sort()
            return(closest_points.loc[input_list])
