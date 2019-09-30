# Copyright [1999-2013] Wellcome Trust Sanger Institute and the EMBL-European Bioinformatics Institute
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script to generate an HTML page containing the variation sources of each species


=head1 CONTACT

  Please email comments or questions to the public Ensembl
  developers list at <dev@ensembl.org>.

  Questions may also be sent to the Ensembl help desk at
  <helpdesk.org>.

=cut


use Bio::EnsEMBL::Registry;
use DBI;
use strict;
use POSIX;
use Getopt::Long;

###############
### Options ###
###############
my ($oldest_version,$newest_version,$json_file,$source_id,$source,$hosts,$logins,$type,$help);
## EG options
my ($site, $etype);

usage() if (!scalar(@ARGV));
use JSON qw(to_json);

GetOptions(
     'oldest_v=i' => \$oldest_version,
     'newest_v=i' => \$newest_version,
     'o=s'        => \$json_file,
     'help!'      => \$help,
     'hosts=s'    => \$hosts,
     'logins=s'   => \$logins,
     'site=s'     => \$site,
     'etype=s'    => \$etype
);

if (!$oldest_version) {
  print "> Error! Please give the Ensembl oldest version you want to retrieve, using the option '-oldest_v' \n";
  usage();
}
if (!$newest_version) {
  print "> Error! Please give the Ensembl newest version you want to retrieve, using the option '-newest_v' \n";
  usage();
}
if (!$json_file) {
  print "> Error! Please give an output file using the option '-o'\n";
  usage();
}
if (!$hosts) {
  print "> Error! Please give the list of host names where the databases are stored using the option '-hosts'\n";
  usage();
}
if (!$logins) {
  print "> Error! Please give the list of logins of the databases using the option '-login'\n";
  usage();
}

usage() if ($help);

my $server_name = 'http://static.ensembl.org';
my $ecaption = 'Ensembl';
my @hostnames  = split /,/, $hosts;
my @loginnames = split /,/, $logins;

if ($site) {
  $server_name = $site;
}
if ($etype) {
  $ecaption .= ' '.ucfirst($etype);
}
# Settings
my $database = "";
my $pswd = "";

my %species_colours = (
                'Bos taurus'        => '#8B2323', # brown 4
                'Canis familiaris'  => '#FF4500', # orangered 1 (orangered)
                'Danio rerio'       => '#000080', # navy
                'Equus caballus'    => '#000000', # black
                'Felis catus'       => '#FF9912', # cadmiumyellow
                'Gallus gallus'     => '#EEEE00', # yellow 2
                'Homo sapiens'      => '#0000EE', # blue 2
                'Mus musculus'      => '#7171C6', # sgi slateblue
                'Ovis aries'        => '#00C957', # emeraldgreen
                'Pongo abelii'      => '#B3EE3A', # olivedrab 2
                'Pongo pygmaeus'    => '#B3EE3A', # olivedrab 2
                'Rattus norvegicus' => '#EE0000', # red 2
                'Sus scrofa'        => '#FF69B4', # hotpink
                'Saccharomyces cerevisiae' => '#CDCD00', # yellow 3
); # 14

my @other_colours = ( '#71C671', # sgi chartreuse
                      '#C1C1C1', # sgi grey 76
                      '#7D26CD', # purple 3
                      '#008080', # teal
                      '#40E0D0', # turquoise
                      '#800080', # purple
                      '#BF3EFF', # darkorchid 1
                      '#E9967A', # darksalmon
                      '#FFB5C5', # pink 1
                      '#696969', # dimgray (gray 42)
                      '#9F79EE', # mediumpurple 2
                      '#DAA520', # goldenrod
                      '#98FB98', # palegreen
                      '#9C661F', # brick
                    ); # 14


############
### Main ###
############

my $json_content = '';
my @species_list;
my %species_data;
my %species_list;
my @categories;

for (my $version=$oldest_version; $version <= $newest_version; $version++) {
  print "#  Version $version\n";
  push (@categories,$version);
  for (my $i=0; $i < scalar(@hostnames);$i++) {
  
    my $sql = qq{SHOW DATABASES LIKE '%variation_$version%'};
    my $sth = get_connection_and_query($database, $hostnames[$i], $loginnames[$i], $sql);

    next if (!$sth);

    # loop over databases
    while (my ($dbname) = $sth->fetchrow_array) {
      next if ($dbname =~ /^master_schema/);
      print "\t$dbname\n";
      $dbname =~ /^(.+)_variation/;
      my $species = $1;
      $species =~ s/_/ /;
      $species =~ /^(\w)(.+)$/;
      $species = uc($1).$2;
      $species_list{$species} = 1 if (!$species_list{$species});
      
      # Get list of sources from the new databases
      my $sql2 = qq{SELECT count(*) FROM variation};
      my $sth2 = get_connection_and_query($dbname, $hostnames[$i], $loginnames[$i], $sql2);
      my $count_var = ($sth2->fetchrow_array)[0];
      $species_data{$species}{$version} = $count_var || 0;
    }
  }
}

my @colours;
my $chart_values;
my @data_values;
my $c_count = 0;
foreach my $sp (sort keys(%species_list)) {
  my @values;
  for (my $version=$oldest_version; $version <= $newest_version; $version++) {
    my $value = ($species_data{$sp}{$version} || $species_data{$sp}{$version} == 0) ? $species_data{$sp}{$version} : 'null';
    push(@values, $value);
  }
  
  # Colours
  my $colour;
  if ($species_colours{$sp}) {
    $colour = $species_colours{$sp};
  }
  else {
    $colour = $other_colours[$c_count];
    $c_count++;
  }
  my %category = ("spe" => $sp, "color" => $colour ,"var_counts" => \@values);
  push @data_values, \%category;
}

my $json_info = to_json(\@data_values);


## HTML/output file ##
open  JSON, "> $json_file" or die "Can't open $json_file : $!";
print JSON qq{{"release_start":$oldest_version,"release_end":$newest_version,"counts":$json_info}};
close(JSON);


# Connects and execute a query
sub get_connection_and_query {
  my $dbname = shift;
  my $hname  = shift;
  my $login  = shift;
  my $sql    = shift;
  
  my ($host, $port) = split /\:/, $hname;

  # DBI connection 
  my $dsn = "DBI:mysql:$dbname:$host:$port";
  my $dbh = DBI->connect($dsn, $login, $pswd) or die "Connection failed";

  my $sth = $dbh->prepare($sql);
  $sth->execute;
  return $sth;
}


sub usage {
  
  print qq{
  Usage: perl var_count.pl [OPTION]
  
  Put all variation sources, for each species, into an HTML document.
  
  Options:

    -help           Print this message
      
    -oldest_v    Ensembl oldest version, e.g. 65 (Required)
    -newest_v    Ensembl newest version, e.g. 77 (Required)
    -o           An HTML output file name (Required)      
    -hosts       Host names where the databases are stored, e.g. ensembldb.ensembl.org  (Required)
    -logins      Login names to the databases (Required)
    -site        The URL of the website (optional)
    -etype       The type of Ensembl, e.g. Plant (optional)
  } . "\n";
  exit(0);
}
