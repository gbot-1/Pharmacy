# Pharmacy Transfer Report System

A comprehensive Python-based system for generating professional pharmacy transfer reports in Belgium. This system automates the process of creating detailed reports for pharmacy relocations, including distance calculations, route mapping, and regulatory compliance documentation.

## Features

- **Automated Report Generation**: Creates professional PDF reports for pharmacy transfers
- **Distance Calculations**: Computes both straight-line and road distances between locations
- **Interactive Maps**: Generates detailed route maps with multiple pharmacy locations
- **Regulatory Compliance**: Ensures transfers comply with Belgian pharmacy regulations (3km radius rule)
- **Protection Zone Analysis**: Creates and analyzes protection zones around pharmacies
- **LaTeX Integration**: Professional document formatting and PDF generation

## System Requirements

### Software Dependencies
- Python 3.7+
- LaTeX distribution (MiKTeX or TeX Live)
- Chrome/Chromium browser
- ChromeDriver

### Python Libraries
```bash
pip install pandas geopandas requests folium matplotlib selenium webdriver-manager polyline shapely
```

### Additional Requirements
- OpenRouteService API Key (required for route calculations)
- Belgian pharmacy database (Excel format)
- Belgian address database (CSV format)

## Project Structure

```
pharmacy_transfer_system/
├── Pharmacie.py                 # Main application entry point
├── template_rapport.tex         # LaTeX template for reports
├── input_function.py           # User input handling functions
├── distance_function.py        # Distance calculation algorithms
├── Create_tex_pdf.py          # LaTeX/PDF generation utilities
├── Map_function.py            # Interactive mapping functions
├── Read_excel.py              # Database loading utilities
├── save_fig.py                # HTML to PNG conversion
├── polygon_drawing.py         # Protection zone analysis
├── Clean_csv.py               # Address database preprocessing
├── data/
│   ├── Lst_Pharmacies_pub_Extended.xlsx
│   ├── adresses_wallonie.csv
│   └── adresses.csv
└── output/
    └── [YEAR]/
        └── [PROJECT_FOLDERS]/
```

## Configuration

### 1. API Setup
Obtain an OpenRouteService API key from [openrouteservice.org](https://openrouteservice.org/) and update the `API_KEY` variable in `Pharmacie.py`:

```python
API_KEY = 'your_openrouteservice_api_key_here'
```

### 2. File Paths
Update the file paths in `Pharmacie.py` to match your system:

```python
FILEPATH = 'path/to/Lst_Pharmacies_pub_Extended.xlsx'
ADRESS_CSV = 'path/to/adresses.csv'
TEMPLATE_PATH = 'path/to/template_rapport.tex'
MAIN_FOLDER = 'path/to/output/directory'
```

### 3. Database Preparation
- Ensure your pharmacy database (Excel) contains required columns:
  - Pharmacy ID, Name, Address, Postal Code, Municipality, X/Y coordinates
- Preprocess the address database using `Clean_csv.py` if needed

## Usage

### Running the System

1. **Start the application**:
   ```bash
   python Pharmacie.py
   ```

2. **Follow the interactive prompts**:
   - Enter pharmacy identification number
   - Provide new implementation coordinates (Lambert 2008)
   - Specify new address details
   - Select date and reference information
   - Choose nearby pharmacies for analysis

3. **Review generated outputs**:
   - Professional PDF report
   - Interactive HTML maps
   - Distance calculation tables
   - Protection zone analysis

### Input Requirements

1. **Pharmacy ID**: Unique identifier from the pharmacy database
2. **New Coordinates**: Lambert 2008 projection coordinates (X, Y)
3. **New Address**: Format: "Street Address, Postal Code, Municipality"
4. **Date/Reference**: Format: "DD/MM/YYYY, Reference_Number"

### Example Session
```
Numéro d'identification de la pharmacie : 12345
Coordonnées X-Y de la nouvelle implentation : 150000.5, 125000.3
Adresse de la nouvelle implentation : Rue de la Paix 15, 5000, Namur
Date et référence du dossier : 15/03/2024, 24.123
```

## Output Files

### Generated Reports
- **PDF Report**: Complete professional transfer report
- **Distance Tables**: Detailed distance calculations in LaTeX format
- **Maps**: PNG format maps showing routes and locations
- **CSV Files**: Distance calculations and pharmacy data

### Folder Structure
```
output/
└── [YEAR]/
    └── [REFERENCE]_[PHARMACY_NAME]/
        ├── [REFERENCE]_[PHARMACY_NAME].pdf
        ├── distance_closest_points_old.csv
        ├── distance_closest_points_new.csv
        ├── map_new_implentation.png
        ├── map_all_pharmacy_old.png
        ├── map_all_pharmacy_new.png
        └── Tex_files/
            ├── [REFERENCE]_[PHARMACY_NAME].tex
            ├── table_old_implentation.tex
            └── table_new_implentation.tex
```

## Key Functions

### Distance Calculations
- `get_planar_distance()`: Calculates straight-line distances
- `get_road_distance_and_geometry()`: Computes route distances via OpenRouteService
- `distance_fly_old_new_implantation()`: Direct distance between old and new locations

### Mapping
- `display_route()`: Creates single route maps
- `display_route_all_pharma()`: Generates comprehensive pharmacy network maps
- `polygon_mid_distance()`: Creates protection zone polygons

### Report Generation
- `generate_main_latex()`: Populates LaTeX templates
- `csv_to_latex_table()`: Converts distance data to LaTeX tables
- `compile_tex_to_pdf()`: Compiles LaTeX to PDF

## Regulatory Compliance

The system ensures compliance with Belgian pharmacy regulations:
- **3km Transfer Rule**: Verifies new location is within 3000m of original
- **Protection Zones**: Analyzes service area coverage
- **Distance Documentation**: Provides detailed measurements for regulatory review

## Troubleshooting

### Common Issues

1. **ChromeDriver Errors**:
   - Ensure Chrome browser is installed
   - ChromeDriver is automatically managed by webdriver-manager

2. **LaTeX Compilation Errors**:
   - Verify LaTeX installation (MiKTeX/TeX Live)
   - Check template file paths and permissions

3. **API Rate Limits**:
   - OpenRouteService has daily request limits
   - Consider implementing request caching for large datasets

4. **Coordinate System Issues**:
   - Ensure coordinates are in Lambert 2008 (EPSG:3812)
   - Verify coordinate transformations are correct

### Performance Optimization

- **Parallel Processing**: Route calculations use ThreadPoolExecutor
- **Caching**: API responses are cached to avoid duplicate requests
- **Batch Operations**: Multiple maps generated in single browser session

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with appropriate tests
4. Submit a pull request

## License

This project is designed for professional use in Belgian pharmacy transfer documentation. Ensure compliance with local regulations and data protection requirements.

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.

---

**Note**: This system handles sensitive pharmacy location data. Ensure proper data protection measures are in place and comply with applicable privacy regulations.