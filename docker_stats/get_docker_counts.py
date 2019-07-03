import sys, os, datetime, shutil
sys.path.append('/homes/lgil/.local/')
import requests

type = ""
if len(sys.argv) > 1:
    type = sys.argv[1]

def get_count(url):
    r = requests.get(url, headers={ "Content-Type" : "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    decoded = r.json()
    return decoded['pull_count'];


# MAIN
datafile_dir = "/homes/lgil/public_html/ensembl/docker"
save_dir = "/homes/lgil/projets/Docker_count/"
backup_dir = "/nfs/panda/ensembl/variation/data/docker_stats/"

repos = ["ensemblorg","willmclaren"]

for repo in repos:

  live_fname = save_dir+"/docker_"+repo+"_ensembl-vep_live.txt"

  fname = save_dir+"/docker_"+repo+"_ensembl-vep.txt"

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

