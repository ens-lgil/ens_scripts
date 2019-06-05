import sys, datetime
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

repos = ["ensemblorg","willmclaren"]

for repo in repos:

  live_fname = datafile_dir+"/docker_"+repo+"_ensembl-vep_live.txt"

  fname = datafile_dir+"/docker_"+repo+"_ensembl-vep.txt"

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
  # Recorded counts
  else:
      record_file = open(fname, 'a')
      record_file.write(line)
      record_file.close()

