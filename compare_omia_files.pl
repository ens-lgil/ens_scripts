#!/usr/bin/env perl

use strict;
use Getopt::Long;

my ($old_omia,$new_omia);

GetOptions('new|n=s'      => \$new_omia,
           'old|o=s'      => \$old_omia
          );
die ("Need to specify the new OMIA directory (-new)") unless($new_omia);
die ("Need to specify the old OMIA directory (-new)") unless($new_omia);
die ("Can't find the directory $new_omia") unless(-d $new_omia);
die ("Can't find the directory $old_omia") unless(-d $old_omia);

my @files;

# Open a directory handle
my $dh;
opendir($dh,$new_omia);
warn("Could not process directory $new_omia") unless (defined($dh));

# Loop over the files in the directory and store the file names of LRG XML files
while (my $file = readdir($dh)) {
 push(@files,$file) if ($file =~ m/^omia_[a-z]+\.txt$/);
}

# Close the dir handle
closedir($dh);

my %results;

foreach my $file (@files) {
  
  $file =~ /^omia_(.+)\.txt$/;
  my $species = $1;
  
  $results{$species} = [];
  
  if (-e "$old_omia/$file") {
  
    my $new_size = -s "$new_omia/$file";
    my $old_size = -s "$new_omia/$file";
    
    push(@{$results{$species}}, 'diff size') if ($new_size != $old_size);
    
    my $new_lines = `cat $new_omia/$file | wc -l`;
    my $old_lines = `cat $old_omia/$file | wc -l`;
    
    push(@{$results{$species}}, 'diff lines') if ($new_lines != $old_lines);
     
  }
  else {
    push(@{$results{$species}}, 'new species');
  }
}


foreach my $species (sort(keys(%results))) {
  my $result = join(',',@{$results{$species}});
  
  if ($result && $result ne '') {
    print "$species: $result\n";
  }
}

