import sys, re
import my_utils

if (len(sys.argv) != 3):
  print("Missing arguments!")
  exit()
  
data_path = sys.argv[1]
data_file = sys.argv[2]

print("PATH: "+data_path);
print("FILE: "+data_file);

data = {}
first_line = re.compile("^gene_symbol")
prefix = 'omia_'
suffix = '.txt'

omia_file = open(data_path+'/'+data_file,'r')
for line in omia_file:
  if (first_line.search(line)):
    continue
  
  line_content = line.split("\t")
  taxo = int(line_content[3])
  
  if (taxo in data):
    data[taxo].append(line)
  else:
    data[taxo] = [line]
omia_file.close()


taxo_list = list(data.keys())
taxo_list.sort()

for taxo_id in taxo_list:
  print("TAXO ID: "+str(taxo_id))

  species_name = my_utils.get_species_names(taxo_id)
  if (species_name!=''):
    species_name = species_name.lower()
    species_name = re.sub(r" ","_",species_name)
    species_name = re.sub(r"'","",species_name)
    species_name = re.sub(r"^domestic_","",species_name)
    print("  SPECIES NAME: "+species_name)
      
    omia_spe_file = open(data_path+'/'+prefix+species_name+suffix,'w')
    for line in data[taxo_id]:
      omia_spe_file.write(line)
    omia_spe_file.close()
  
