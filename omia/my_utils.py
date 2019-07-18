import sys, re
sys.path.append('/homes/lgil/.local/')
import requests

server = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id='
ext = "&retmode=xml"

def get_species_names(taxon_id):
    """Returns species name from taxonomy ID"""
    species_name = ''
    req = requests.get(server+str(taxon_id)+ext)
    if (req.status_code == 200):
      species_name_search = re.search('<GenbankCommonName>(.+)<\/GenbankCommonName>', req.text, re.IGNORECASE)
      if species_name_search:
        species_name = species_name_search.group(1)
    return species_name
        
