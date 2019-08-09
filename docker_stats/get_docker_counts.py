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

import sys, os, getopt,datetime, shutil
# Get home directory
homedir = os.path.expanduser("~")
sys.path.append(homedir+'/.local/')
import requests

datafile_dir = ""
tmp_dir = ""
type = ""
backup_dir = "/nfs/panda/ensembl/variation/data/docker_stats/"

msg = '''python3 get_docker_counts.py -d <data_dir> -t <tmp_dir> -y <type>

  - <data_dir> : directory where you want to store the text files
  - <tmp_dir>  : temporary directory to copy the previous data files and edit them
  - <type>     : only use it with the value 'live' for the hourly check of the counts (optional)
'''

# Get the pulls count
def get_count(url):
    r = requests.get(url, headers={ "Content-Type" : "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    decoded = r.json()
    return decoded['pull_count'];


# Fetch and parse the parameters
def get_parameters(argv):

    global datafile_dir, tmp_dir, type, msg

    # Parse options
    try:
        opts, args = getopt.getopt(argv,"d:t:y:",["datadir=","tmpdir=","type="])
    except getopt.GetoptError:
        print (msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d", "--datadir"):
           datafile_dir = arg
        elif opt in ("-t", "--tmpdir"):
           tmp_dir = arg
        elif opt in ("-y", "--type"):
           type = arg

    # Handling missing options
    error_msg = ''
    if (datafile_dir==''):
        error_msg += "ERROR: option '--datadir' (-d) is missing.\n"
    if (tmp_dir==''):
        error_msg += "ERROR: option '--tmpdir' (-t) is missing.\n"
    if (type!='' and type!='live'):
        error_msg += "ERROR: option '--type' (-y) only allows the value 'live'.\n"
    if (error_msg!=''):
        print(error_msg)
        sys.exit(2)


#------#
# MAIN #
#------#

if len(sys.argv) > 1:
    get_parameters(sys.argv[1:])
else:
    print("ERROR: missing options!\n\nPlease, use the following options:\n\n"+msg)
    sys.exit(2)


repos = ["ensemblorg","willmclaren"]

for repo in repos:

    server = "https://hub.docker.com/v2/repositories"
    ext = "/"+repo+"/ensembl-vep/"

    url = server + ext

    pulls = get_count(url)

    localtime = '{0:%d-%m-%Y %H:%M}'.format(datetime.datetime.now())

    line = str(pulls)+"\t"+localtime+"\n"

    # Current (hourly) count
    if type == 'live':
        live_fname = tmp_dir+"/docker_"+repo+"_ensembl-vep_live.txt"
        
        live_file = open(live_fname, 'w')
        live_file.write(line)
        live_file.close()
        if (os.path.isfile(live_fname) and os.path.isdir(datafile_dir)):
            shutil.copy2(live_fname,datafile_dir)
    # Recorded (daily) count
    else:
        fname = "docker_"+repo+"_ensembl-vep.txt"
        tmp_fname = tmp_dir+"/"+fname
        bak_fname = backup_dir+"/"+fname

        # 1 - Copy from backup to tmp directory
        if (os.path.isfile(bak_fname)):
            shutil.copy2(bak_fname,tmp_dir)
        else:
            print("Can't find the backed up data file containing the daily pulls count! It should be in the '"+backup_dir+"' directory")
            exit(2)
        
        # 2 - Update file in tmp directory
        record_file = open(tmp_fname, 'a')
        record_file.write(line)
        record_file.close()
        
        # 3 - Copy file to backup and web directories
        if (os.path.isfile(tmp_fname)):
            if (os.path.isdir(datafile_dir)):
                shutil.copy2(tmp_fname,datafile_dir)
            if (os.path.isdir(backup_dir)):
                shutil.copy2(tmp_fname,backup_dir)

