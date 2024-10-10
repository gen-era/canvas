import openpyxl
def generate_data_list(file_path):
    # Define corresponding headers for each field
    prot_id_list = ['Genetik Protokol No', 'Protokol No']
    inst_list = ['Kurum', 'Bölge']
    arrival_date = ['Kayıt Tarihi', 'Test Eklenme Tarihi']
    sample_type = ['Test Adı', 'Çalışma Yöntemi']

    # Load the workbook and select the active worksheet
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    # Read the header row (assuming the first row is the header)
    headers = []
    for cell in ws[1]:
        headers.append(cell.value)

    # Function to find the column index for a given list of possible headers
    def find_column(header_options):
        for option in header_options:
            if option in headers:
                return headers.index(option) + 1  # openpyxl is 1-indexed
        return None

    # Find column indices for each field
    prot_id_col = find_column(prot_id_list)
    inst_col = find_column(inst_list)
    arrival_date_col = find_column(arrival_date)
    sample_type_col = find_column(sample_type)

    # Check if all required columns are found
    required_columns = {
        'prot_id': prot_id_col,
        'inst': inst_col,
        'arrival_date': arrival_date_col,
        'sample_type': sample_type_col
    }

    missing_columns = [key for key, val in required_columns.items() if val is None]
    if missing_columns:
        raise ValueError(f"Missing columns in the Excel file: {', '.join(missing_columns)}")

    data_list = []

    # Iterate over the rows starting from the second row
    for row in ws.iter_rows(min_row=2, values_only=True):
        # Extract data based on column indices
        prot_id = row[prot_id_col - 1]
        inst = row[inst_col - 1]
        arrival = row[arrival_date_col - 1]
        sample = row[sample_type_col - 1]

        # Create a dictionary for the current row
        row_dict = {
            'prot_id': prot_id,
            'inst': inst,
            'arrival_date': arrival,
            'sample_type': sample
        }

        data_list.append(row_dict)

    return data_list

