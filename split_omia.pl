use strict;
use warnings;
 
use HTTP::Tiny;
 
my $path = $ARGV[0];
my $file = $ARGV[1];
die ("Can't find the path $path") unless(-d $path);
die ("Can't find the file $path/$file") unless(-e "$path/$file");

my $prefix = 'omia_';
my $suffix = '.txt';

my $http = HTTP::Tiny->new();
 
my $server = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id=';
my $ext = "&retmode=xml";

my %data;

my %species = (
  9685  => 'cat',
  9031  => 'chicken',
  9598  => 'chimpanzee',
  9913  => 'cow',
  9615  => 'dog',
  61853 => 'gibbon',
  9796  => 'horse',
  9544  => 'macaque',
  10090 => 'mouse',
  13616 => 'opossum',
  9601  => 'orangutan',
  9825  => 'pig', # Sus scrofa domesticus
  9258  => 'platypus',
  10116 => 'rat',
  9940  => 'sheep',
  99883 => 'tetraodon',
  9103  => 'turkey',
  59729 => 'zebra_finch',
  7955  => 'zebrafish'
);

open F, "< $path/$file" or die $!;
while(<F>) {
  chomp ($_);
  next if ($_ =~ /^gene_symbol/);
  my $line = $_;
  my @line_content = split("\t",$line);
  my $taxo = $line_content[3];
  if ($data{$taxo}) {
    push(@{$data{$taxo}}, $line);
  }
  else {
    $data{$taxo} = [$line];
  }
}
close(F);

foreach my $taxo_id (sort(keys(%data))) {
  my $id = $taxo_id;
  
  if ($species{$taxo_id}) {
    $id = $species{$taxo_id};
  }
  else {
    my $response = $http->get($server.$taxo_id.$ext);
   
    if ($response->{success} && length($response->{content})) {
      my $content = $response->{content};
      if ($content =~ /<GenbankCommonName>(.+)<\/GenbankCommonName>/) {
        $id = $1;
      }
    }
  }

  $id = lc($id);
  $id =~ s/ /_/g;
  $id =~ s/^domestic_//g;

  open OUT, "> $path/$prefix$id$suffix" or die $!;
  foreach my $line (@{$data{$taxo_id}}) {
    print OUT "$line\n";
  }
  close(OUT);
}

