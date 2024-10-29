import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showerror, showinfo
from tkinter.colorchooser import askcolor
import simplejson as json
import requests #to query google
from bs4 import BeautifulSoup  #to query google
import re



##########################################################################################################
#
#                MITRE ATTACK MAPPER
#                     Author:   Julie BRUNIAS
#                     Produced: 2024
#
#
#                  How it works:
#                     - Search a keyword
#                     - Choose a color
#                     - Choose an output filename
#                     - Load Enterprise.json
#
#                     Build the map within couple of seconds 
#
##########################################################################################################


#variable declaration
unique_list = []
results = []

def find_id_by_description(json_data, target_description):
    try:
        # Read the JSON data
        with open(json_data, "r", encoding="utf-8") as json_file:
            parsed_data = json.load(json_file)
            matching_external_ids = []
            print("")
            print("")
            
            # Search for the object with the specified description containing '.bash_history'
            for obj in parsed_data.get("objects", []):
                external_refs = obj.get("external_references", [])
                
                for ref in external_refs:
                    ref_description = ref.get("description", "").lower().strip()
                    
                    
                    # Check if the target description is in the ref description
                    if target_description.lower() in ref_description:
                        # Retrieve the external ID (if available)
                        external_id = ref.get("external_id")
                        external_id2 = external_refs[0].get("external_id")
                        # Append the external ID to the array
                        if external_id2:
                            print(f"in external_id2 LOOP")
                            matching_external_ids.append(external_id2)
                            # Retrieve the object ID
                            obj_id = obj.get("id")
                            print("")
                            print(f"Match found! External ID: {external_id2}, Object ID: {obj_id}")
                            print("")
                            print("")
                        
                            
            # If matching external IDs are found, make sure there are no duplicates
            if matching_external_ids:
                
                #print(f"FULL ARRAY: {matching_external_ids}")
                unique_list = list(set(matching_external_ids))
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++    UNIQUE LIST    +++++++++++++++++++++++")
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(unique_list)
                
                #return matching_external_ids
                return unique_list
            else:
                print(f"No matching object found for description containing '{target_description}'.")
                return None

                    
    except FileNotFoundError:
        print(f"File '{json_data}' not found.")
        return None, None



def change_color():
    global color
    color = askcolor(title="Tkinter Color Chooser")
    return color
    
    

def select_file():
    global filename
    filetypes = [('JSON files', '*.json'), ('All files', '*.*')]
    filename = filedialog.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
    return filename


def verify_text_entry():
    # Check if a Entreprise.json has been selected
    if not filename:
        showerror(title='Error', message='No file selected!')
        
    # Check if a output filename has been entered
    output_path = output_entry.get()   
    if not output_path:
        print("Please choose an output file.")
        showerror(title='Error', message='Please enter an output filename !')
        return
    
    # Check if a keyword has been entered
    keyword = keyword_entry.get()
    if not keyword:
        print("Please enter a keyword.")
        showerror(title='Error', message='Please enter a keyword !')
        return
   
    
    # Check if a color has been chosen
    if not color:
        print("Please choose a color.")
        showerror(title='Error', message='Please choose a color !')
        return
    
    # All checks passed, perform search
    print(f"Searching for '{keyword}' in file '{filename}' with color '{color[1]}' and writing outout to {output_path}'.")
    

    
    json_data = filename  #filename is declared above
    unique_list = find_id_by_description(json_data, keyword)
    
    
    

    print("")
    print("")
    print("UNIQUE LIST HERE:", unique_list)
    initial_list = list(set(unique_list))
    print("")
    print("")
    print("Initial LIST:", initial_list)
    TTP_not_complete = []
    list_to_check = []
    t_values_in_C = set() # list of TTP (Techniques) found in corresponding Campaign (eg C0015)
    t_values_in_G = set() # list of TTP (Techniques) found in corresponding Group (eg G0034)
    t_values_in_S = set() # list of TTP (Techniques) found in corresponding Software (eg S0583)
    complete_technique_ids = set()

    
    
    def parse_and_filter_list(input_list):
        # Create a set to store the filtered items
        cleaned_list = []

        # Iterate over each item in the input list
        for item in input_list:
            

            # Check if T1562 belongs to anything in the code list
            if any(code.startswith(item + ".") for code in input_list):
                pass
            else:
                cleaned_list.append(item)


        # Print the updated special list
        print("")
        print("")
        print("Cleaned list:", cleaned_list)
        
        return cleaned_list
        

    # Iterate over each item in the initial list
    for item in initial_list:
        if item.startswith('T'):
            # If the item starts with 'T', add it to TTP_not_complete list
            TTP_not_complete.append(item)
        else:
            # Otherwise, add it to list_to_check list
            list_to_check.append(item)

    # Print the results
    print(f"Initial List:: {initial_list}")
    print("")
    print("")
    print(f"TTP_not_complete list: {TTP_not_complete}")
    print("")
    print("")    
    print(f"list_to_check list: {list_to_check}")
    print("")
    print("") 

    
    # Iterate over each item in the list_to_check
    for item in list_to_check:
        # if CAMPAIGN
        if item.startswith('C'):

            print("")
            print("")
            print(f"CHECK {item} is LIKE Cxxx")
            # Perform a Mitre Attack search
            MitreAttack_search_url = f"http://attack.mitre.org/campaigns/{item}"
            print("")
            print("")
            print(f"MITRE ATTACK SEARCH URL: {MitreAttack_search_url}\n\n")
            response = requests.get(MitreAttack_search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            technique_links = soup.find_all('a', href=re.compile(r'/techniques/'))
            print("")
            print("")
            print(f"TECHNIQUE LINKS: {technique_links}")
                         
            if technique_links:
                for technique in technique_links:
                    result_url = technique['href']                     
                    print(f"RESULT URL: {result_url}")           #RESULT URL: /techniques/T1059/003
                    result_match_technique = re.search(r'/techniques/T(\d{4})', result_url)
                    result_match_sub_technique = re.search(r'/techniques/T(\d{4})/(\d{3})', result_url)
                    print("")
                    print("")
                    print(f"RESULT MATCH TECHNIQUE: {result_match_technique}")
                    print("")
                    print("")
                    print(f"RESULT MATCH SUB TECHNIQUE: {result_match_sub_technique}")
                    print("")
                    print("")
                    if result_match_technique:
                        technique_id = result_match_technique.group(1)  # Extract the first group (technique ID)
                        result = f"T{technique_id}"
                        t_values_in_C.add(result)
                        print(f"RESULT TECHNIQUE: {result}")
                            
                    if result_match_sub_technique:
                        technique_id, sub_technique_id = result_match_sub_technique.groups()
                        if sub_technique_id.startswith("0"):
                            result = f"T{technique_id}.{sub_technique_id}"
                            t_values_in_C.add(result)
                            print(f"RESULT SUB TECHNIQUE: {result}")
                        else:
                            result = f"T{technique_id}"
                            t_values_in_C.add(result)
                            print(f"RESULT TECHNIQUE: {result}")

                    else:
                        print("No relevant link found in the search results.")
                        
        
        # if GROUP 
        elif item.startswith('G'):
            print("")
            print("")
            print(f"CHECK {item} is LIKE Gxxx")
            
            # Perform a Mitre Attack search
            MitreAttack_search_url = f"http://attack.mitre.org/groups/{item}"
            print("")
            print("")
            print(f"MITRE ATTACK SEARCH URL : {MitreAttack_search_url}")
            response = requests.get(MitreAttack_search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            technique_links = soup.find_all('a', href=re.compile(r'/techniques/'))
            print("")
            print("")
            print(f"TECHNIQUE LINKS: {technique_links}")
                         
            if technique_links:
                for technique in technique_links:
                    result_url = technique['href']                     
                    print(f"RESULT URL: {result_url}")           #RESULT URL: /techniques/T1059/003
                    result_match_technique = re.search(r'/techniques/T(\d{4})', result_url)
                    result_match_sub_technique = re.search(r'/techniques/T(\d{4})/(\d{3})', result_url)
                    print("")
                    print("")
                    print(f"RESULT MATCH TECHNIQUE: {result_match_technique}")
                    print("")
                    print("")
                    print(f"RESULT MATCH SUB TECHNIQUE: {result_match_sub_technique}")
                    print("")
                    print("")
                    if result_match_technique:
                        technique_id = result_match_technique.group(1)  # Extract the first group (technique ID)
                        result = f"T{technique_id}"
                        t_values_in_G.add(result)
                        print(f"RESULT TECHNIQUE: {result}")
                            
                    if result_match_sub_technique:
                        technique_id, sub_technique_id = result_match_sub_technique.groups()
                        if sub_technique_id.startswith("0"):
                            result = f"T{technique_id}.{sub_technique_id}"
                            t_values_in_G.add(result)
                            print(f"RESULT SUB TECHNIQUE: {result}")
                        else:
                            result = f"T{technique_id}"
                            t_values_in_G.add(result)
                            print(f"RESULT TECHNIQUE: {result}")

                    else:
                        print("No relevant link found in the search results.")

        
        # if SOFTWARE
        elif item.startswith('S'):
            print(f"CHECK {item} is LIKE Sxxx")
            # Perform a Mitre Attack search
            MitreAttack_search_url = f"http://attack.mitre.org/software/{item}"
            print("")
            print("")
            print(f"MITRE ATTACK SEARCH URL : {MitreAttack_search_url}")
            response = requests.get(MitreAttack_search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            technique_links = soup.find_all('a', href=re.compile(r'/techniques/'))
            print("")
            print("")
            print(f"TECHNIQUE LINKS: {technique_links}")
                         
            if technique_links:
                for technique in technique_links:
                    result_url = technique['href']                     
                    print(f"RESULT URL: {result_url}")           #RESULT URL: /techniques/T1059/003
                    result_match_technique = re.search(r'/techniques/T(\d{4})', result_url)
                    result_match_sub_technique = re.search(r'/techniques/T(\d{4})/(\d{3})', result_url)
                    print("")
                    print("")
                    print(f"RESULT MATCH TECHNIQUE: {result_match_technique}")
                    print("")
                    print("")
                    print(f"RESULT MATCH SUB TECHNIQUE: {result_match_sub_technique}")
                    print("")
                    print("")
                    if result_match_technique:
                        technique_id = result_match_technique.group(1)  # Extract the first group (technique ID)
                        result = f"T{technique_id}"
                        t_values_in_S.add(result)
                        print(f"RESULT TECHNIQUE: {result}")
                            
                    if result_match_sub_technique:
                        technique_id, sub_technique_id = result_match_sub_technique.groups()
                        if sub_technique_id.startswith("0"):
                            result = f"T{technique_id}.{sub_technique_id}"
                            t_values_in_S.add(result)
                            print(f"RESULT SUB TECHNIQUE: {result}")
                        else:
                            result = f"T{technique_id}"
                            t_values_in_S.add(result)
                            print(f"RESULT TECHNIQUE: {result}")

                    else:
                        print("No relevant link found in the search results.")
            
        # NEITHER CAMPAIGN OR GROUP OR SOFTWARE, so its an ERROR
        else:
            print(f"ERROR {item} is NOT either Cxxx or Gxxx or Sxxx:")
            
        
    
    # list all TTPs listed under the returned URL from Mitre
    print("")
    print("")
    print(f"The T values for CAMPAIGN found in the HTML are: {t_values_in_C}")
    print("")
    print("")
    # Call the function to parse and filter the list
    filtered_list_in_C = parse_and_filter_list(t_values_in_C)
    print("")
    print(f"FILTERED C_TECHNIQUES: {filtered_list_in_C}")
    print("")
    print("")         
    print(f"The T values for GROUP found in the HTML are: {t_values_in_G}")
    print("")
    print("")
    # Call the function to parse and filter the list
    filtered_list_in_G = parse_and_filter_list(t_values_in_G)
    print("")
    print(f"FILTERED G_TECHNIQUES: {filtered_list_in_G}")
    print("")
    print("")  
    print(f"The T values for SOFTWARE found in the HTML are: {t_values_in_S}")
    print("")
    print("") 
   # Call the function to parse and filter the list
    filtered_list_in_S = parse_and_filter_list(t_values_in_S)
    print("")
    # Print the filtered list
    print(f"FILTERED S_TECHNIQUES: {filtered_list_in_S}")
    print("")
    print("")
    
    
    if filtered_list_in_C and filtered_list_in_G and filtered_list_in_S:
        print("ok")
        # If non empty merge them:
        merged_filtered_lists = filtered_list_in_C + filtered_list_in_G + filtered_list_in_S
        print(f"MERGED 1:  {merged_filtered_lists}")
        print("")
        print("")
        # By creating a SET from a LIST, it automatically removes any duplicate values:
        merged_filtered_lists_without_duplicates = list(set(merged_filtered_lists))
        print(f"MERGED 1 NO DUPLICATES:  {merged_filtered_lists_without_duplicates}")
        # Then add merged list to TTP list (merge both)
        merged_filtered_lists_AND_TTP_not_complete = merged_filtered_lists_without_duplicates + TTP_not_complete
        print("")
        print("")
        print(f"MERGED 2:  {merged_filtered_lists_AND_TTP_not_complete}")
        # Remove duplicates if any
        merged_filtered_lists_without_duplicates_AND_TTP_not_complete = list(set(merged_filtered_lists_AND_TTP_not_complete))
        print("")
        print("")
        print(f"MERGED 2 NO DUPLICATES:  {merged_filtered_lists_without_duplicates_AND_TTP_not_complete}")
        # Then create JSON map from the final_list

        technique_ids = merged_filtered_lists_without_duplicates_AND_TTP_not_complete
        techniques_list = []
        
        
        # Iterate over each technique ID, color is retrieved from GUI
        for technique_id in technique_ids:
            technique_dict = {
                "techniqueID": technique_id,
                #"color": color,
                "color": color[1],
                "comment": "",
                "enabled": True,
                "metadata": [],
                "links": [],
                "showSubtechniques": True
            }
            techniques_list.append(technique_dict)
        print("")
        print("")
        print(f"TECHNIQUES LIST:  {techniques_list}")


        # Additional data to be added at the end of the JSON
        end_data = {
            "gradient": {
            "colors": ["#ff6666ff", "#ffe766ff", "#8ec843ff"],
            "minValue": 0,
            "maxValue": 100
            },
            "legendItems": [],
            "metadata": [],
            "links": [],
            "showTacticRowBackground": False,
            "tacticRowBackground": "#dddddd",
            "selectTechniquesAcrossTactics": True,
            "selectSubtechniquesWithParent": False,
            "selectVisibleTechniques": False
        }

        # Beginning of file to be written to the JSON file
        # Combine the technique data and additional data
        combined_data = {
            "name": "Windows_Linux_Mac_Ransomware",
            "versions": {
                "attack": "15",
                "navigator": "5.0.1",
                "layer": "4.5"
            },
            "domain": "enterprise-attack",
            "description": "",
            "filters": {
                "platforms": [
                "Windows",
                "Linux",
                "macOS",
                "Network",
                "PRE",
                "Containers",
                "Office 365",
                "SaaS",
                "Google Workspace",
                "IaaS",
                "Azure AD"
                ]
            },
            "sorting": 0,
            "layout": {
                "layout": "side",
                "aggregateFunction": "average",
                "showID": False,
                "showName": True,
                "showAggregateScores": False,
                "countUnscored": False,
                "expandedSubtechniques": "all"
            },
            "hideDisabled": False,
            "techniques": techniques_list
        }

        # Add the end data to the combined data
        combined_data.update(end_data)
        print("")
        print("")
        print(f"COMBINED DATA:  {combined_data}")


        # Write the data to the JSON file
        with open(output_path, "w") as file:
            json.dump(combined_data, file, indent=4)

        print("")
        print("")
        print(f"Data has been written to {output_path}")
        
    else:
        print(" !!! ABORT !!! Not all lists are non-empty.")
        exit



root = tk.Tk()
root.title('Mitre Att&ck Keyword Search')
root.configure(bg="#1D2951")
root.geometry("1000x400")

empty_label = tk.Label(root, text="", bg="#1D2951")
empty_label.grid(row=0, column=0, padx=10, pady=5)
title_label = tk.Label(root, text="Search for $keyword in all Enterprise.JSON" +
                                 " and list all TTPs associated with $Keyword," +
                                 " then build a map showing only those TTPs",
                      font=("Helvetica", 11, "bold"), fg="white", bg="#1D2951")
title_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

empty_label2 = tk.Label(root, text="", bg="#1D2951")
empty_label2.grid(row=2, column=0, padx=10, pady=5)

empty_label3 = tk.Label(root, text="", bg="#1D2951")
empty_label3.grid(row=3, column=0, padx=10, pady=5)
# Open button for file selection

group_frame1 = tk.Frame(root, bg="#1D2951")
group_frame1.grid(row=4, column=1)

text_open = tk.Label(group_frame1, text="Load : ", font=("Helvetica", 11, "bold"), fg="white", bg="#1D2951")
text_open.grid(row=4, column=0, sticky="w")


open_button = ttk.Button(group_frame1, text='Open Enterprise JSON File', command=select_file)
open_button.grid(row=4, column=1, padx=10, pady=5)

# Text entry
group_frame2 = tk.Frame(root, bg="#1D2951")
group_frame2.grid(row=4, column=0)
keyword_label = tk.Label(group_frame2, text="Type a keyword : ", font=("Helvetica", 11, "bold"), fg="white", bg="#1D2951")

keyword_label.grid(row=0, column=0, sticky="w")
keyword_entry = ttk.Entry(group_frame2)

keyword_entry.grid(row=0, column=1, padx=10)

empty_label4 = tk.Label(root, text="", bg="#1D2951")
empty_label4.grid(row=5, column=0, padx=10, pady=5)

# Text entry
group_frame3 = tk.Frame(root, bg="#1D2951")
group_frame3.grid(row=6, column=0)
text_output = tk.Label(group_frame3, text="Output filename : ", font=("Helvetica", 11, "bold"), fg="white", bg="#1D2951")
text_output.grid(row=0, column=0, sticky="w")
output_entry = ttk.Entry(group_frame3)
output_entry.grid(row=0, column=1, padx=10)

# Color Chooser
group_frame4 = tk.Frame(root, bg="#1D2951")
group_frame4.grid(row=6, column=1)
text_color = tk.Label(group_frame4, text="Output color : ", font=("Helvetica", 11, "bold"), fg="white", bg="#1D2951")
text_color.grid(row=6, column=0)
color_button = ttk.Button(group_frame4, text="Select a Color", command=change_color)
color_button.grid(row=6, column=1)

empty_label7 = tk.Label(root, text="", bg="#1D2951")
empty_label7.grid(row=7, column=0, padx=10, pady=5)
empty_label8 = tk.Label(root, text="", bg="#1D2951")
empty_label8.grid(row=8, column=0, padx=10, pady=5)
empty_label5 = tk.Label(root, text="", bg="#1D2951")
empty_label5.grid(row=6, column=0, padx=10, pady=5)

# Verify button for text entry
search_button = ttk.Button(root, text='Search', command=verify_text_entry)
search_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
