import sys, os, getopt,datetime, shutil
# Get home directory
homedir = os.path.expanduser("~")
sys.path.append(homedir+'/.local/')
import requests

datafile_dir = ""
tmp_dir = ""
type = ""
backup_dir = "/nfs/panda/ensembl/variation/data/docker_stats/"

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
    msg = 'get_docker_counts.py -d <data_dir> -t <tmp_dir> -y <type>'
    global datafile_dir, tmp_dir, type

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


repos = ["ensemblorg","willmclaren"]

for repo in repos:

  live_fname = tmp_dir+"/test_docker_"+repo+"_ensembl-vep_live.txt"

  fname = tmp_dir+"/test_docker_"+repo+"_ensembl-vep.txt"

  server = "https://hub.docker.com/v2/repositories"
  ext = "/"+repo+"/ensembl-vep/"

  url = server + ext

  pulls = get_count(url)

  localtime = '{0:%d-%m-%Y %H:%M}'.format(datetime.datetime.now())

  line = str(pulls)+"\t"+localtime+"\n"

  # Current count
  if type == 'live':
      live_file = open(live_fname, 'w')
      live_file.write(line)
      live_file.close()
      if (os.path.isfile(live_fname) and os.path.isdir(datafile_dir)):
        shutil.copy2(live_fname,datafile_dir)
  # Recorded counts
  else:
      record_file = open(fname, 'a')
      record_file.write(line)
      record_file.close()
      if (os.path.isfile(fname)):
        if (os.path.isdir(datafile_dir)):
          shutil.copy2(fname,datafile_dir)
        if (os.path.isdir(backup_dir)):
          shutil.copy2(fname,backup_dir)

