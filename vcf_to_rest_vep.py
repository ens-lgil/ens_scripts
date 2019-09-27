"""
   Copyright [1999-2015] Wellcome Trust Sanger Institute and the EMBL-European Bioinformatics Institute
   Copyright [2016-2019] EMBL-European Bioinformatics Institute
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import requests, sys, os, re, json

# Global variables
server  = "http://rest.ensembl.org"
ext     = "/vep/homo_sapiens/region"
headers = { "Content-Type" : "application/json", "Accept" : "application/json"}

max_variants_per_rest_call = 200

json_output = ''


def parse_vcf (input_file):
    """ Read VCF file to extract data and organise it correctly for the Ensembl API REST call(s) """
    global max_post

    input_list = []
    count_variants = 0
    rest_calls = 1
    with open (input_file, "r") as fileHandler:
        for line in fileHandler:
            if (line.startswith('#')):
                continue
            elif (count_variants == max_variants_per_rest_call):
                print("REST query #"+str(rest_calls)+" ("+str(len(input_list))+" variants)")
                send_rest_query(input_list)
                input_list = []
                count_variants = 0
                rest_calls = rest_calls+1
            # Parse the VCF line
            line_content = line.strip()
            line_parts = line_content.split("\t")
            line_vcf = ''
            # Rebuild the VCF input with only the useful columns and a space as separator
            for col in range(5):
                line_vcf = (line_vcf == '') and line_parts[col] or line_vcf+" "+line_parts[col]
            input_list.append(line_vcf)
            count_variants = count_variants + 1

    if (len(input_list) != 0):
        print("REST query #"+str(rest_calls)+" ("+str(len(input_list))+" variants)")
        send_rest_query(input_list)


def send_rest_query (input_data):
    """ Send the input query to the Ensembl REST API and retrieve the JSON output """
    global server, ext, headers, json_output

    input_data_string = '"'+'","'.join(input_data)+'"'
    # REST call
    r = requests.post(server+ext, headers=headers, data='{ "variants" : [ '+input_data_string+' ] }')
    if not r.ok:
        r.raise_for_status()
        sys.exit()

    # Decode JSON output
    decoded = r.json()
    json_data = repr(decoded)

    # Print indented JSON output
    #json_indented = json.dumps(decoded, sort_keys=True, indent=4)
    #print(json_indented)

    # Append JSON result of the current REST API call to the main JSON output
    if (json_output != ''):
        json_data   = re.sub(r'^\[',',',json_data)
        json_output = re.sub(r'\]$','',json_output)
    json_output = json_output + json_data


def write_output(json_output_file):
    """ Write JSON results to the JSON output file """
    global json_output

    # Cosmetic changes to make it a bit more human readable
    #json_output = re.sub(r'^\[','[\n\t',json_output)
    #json_output = re.sub(r'\}, \{','},\n\t{',json_output)
    #json_output = re.sub(r'\]$','\n]',json_output)

    output_file = open(json_output_file,"w")
    output_file.write(json_output)
    output_file.close()


def main():
    """ Main method fetching the VCF input file, reading it line by line and sending the data to the Ensembl REST API """
    global json_output

    if len(sys.argv) < 3:
        msg = "python3 "+sys.argv[0]+" <path_to_vcf_input_file> <path_to_json_output_file>"
        sys.exit("ERROR: missing arguments!\n\nPlease, use the following options:\n"+msg)

    vcf_file = sys.argv[1];
    json_output_file = sys.argv[2]

    # File doesn't exist
    if not(os.path.isfile(vcf_file)):
        sys.exit("ERROR: file '"+vcf_file+"' doesn't exist")

    parse_vcf(vcf_file)
    write_output(json_output_file)

## Main ##
if __name__ == "__main__":
    main()
