import json

# File path (Change this to your actual location of the output.txt)
outfilep = r"C:\Users\dyani\Desktop\Intern\ArmourZero_Intern\Login Automation\output.txt"

# Initialize variables
Usrnm_varNAME = None
Passw_varNAME = None

def extract_names():
    global Usrnm_varNAME, Passw_varNAME
    
    with open(outfilep, "r") as file:
        content = json.load(file) 

    namecount = 0  # Counter for "name" entries

    # Loop through the data
    for line in content:
        if "name" in line:
            namecount += 1
            if namecount == 1:  # Username/Email "name"
                Usrnm_varNAME = line["name"]
            elif namecount == 2:  # Password "name"
                Passw_varNAME = line["name"]
                break  # Exit loop once both variables are found

    # Validate that both variables were found
    if Usrnm_varNAME is None or Passw_varNAME is None:
        raise ValueError("Failed to extract both 'name' fields from the file")
