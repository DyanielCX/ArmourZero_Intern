import json

# File path (Update this to the actual location of your JSON file)
outfilep = r"C:\Users\dyani\Desktop\Intern Script\ArmourZero_Intern\Login Automation\output.txt"

# Initialize variables for import
Usrnm_varNAME = None
Passw_varNAME = None

def extract_names():
    global Usrnm_varNAME, Passw_varNAME
    
    with open(outfilep, "r") as file:
        content = json.load(file)  # Parses JSON into a Python list of dictionaries

    namecount = 0  # Counter for "name" entries

    # Loop through the data
    for line in content:
        if "name" in line:
            namecount += 1
            if namecount == 1:  # First "name"
                Usrnm_varNAME = line["name"]
            elif namecount == 2:  # Second "name"
                Passw_varNAME = line["name"]
                break  # Exit loop once both variables are found

    # Validate that both variables were found
    if Usrnm_varNAME is None or Passw_varNAME is None:
        raise ValueError("Failed to extract both 'name' fields from the file")
