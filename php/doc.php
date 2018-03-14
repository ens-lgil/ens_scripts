<?php

  $doc_id = '';
  $title = 'Documentation reports';
  
  if ($_GET['doc']) {
    $doc_id = $_GET['doc'];
    $doc_label = ucfirst($doc_id);
    $title = "Documentation of ".str_replace('_', ' ', $doc_label);
  }
  
  echo <<<EOF
  <html>
    <head>
      <title>$title</title>
      <!--<link rel="stylesheet" type="text/css" media="all" href="https://static.ensembl.org/minified/02afbeb954298bb8764293594499fc0d.css"/>
      <link rel="stylesheet" type="text/css" media="all" href="https://static.ensembl.org/minified/54ed15bdf949e6883441eb956802019b.image.css"/>-->
      
      <link rel="stylesheet" type="text/css" media="all" href="staging.css"/>
      <link rel="stylesheet" type="text/css" media="all" href="staging.image.css"/>
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
      <script>
        $( document ).ready(function() {
          //var url_root = 'https://static.ensembl.org';
          var url_root = '.';
          $("img").each(function( index ) {
            var img_src = $(this).attr('src');
            if (img_src.match(/^\//)) {
              $(this).attr('src', url_root+img_src);
            }
          });
        });
      </script>
    </head>
    <body style="padding: 5px 10px">
EOF;
  
  $select_list  = array();
  if ($handle = opendir('./')) {
    while (false !== ($file = readdir($handle))) {
      if (preg_match('/^(\w+)\.html$/',$file,$matches)) {
        $doc = $matches[1];
        $label_array  = split('_',$doc);
        $report_label = implode(' ',$label_array);
        $report_label = ucfirst($report_label);
        $select_list[$doc] = $report_label;
      }
    }
    natsort($select_list);
    closedir($handle);
  }
  
  echo <<<EOF
  <div style="padding:2px 6px;background-color:#000">
    <div class="glyphicon glyphicon glyphicon-list" style="float:left;color:#FFF;padding:6px 8px 6px 2px;font-size:18px"></div>
    <div style="float:left;padding:6px 0px;color:#FFF">List of available documentation:</div>
    <div style="float:left;padding:6px 0px;margin-left:10px">
      <form style="margin-bottom:0px">
EOF;
  $space = '        ';
  echo "$space<select name=\"doc\" onchange='this.form.submit()'>";
  echo "<option value=\"\">-</option>";
  foreach ($select_list as $report => $report_label) {
    $selected = '';
    if ($report == $doc_id) {
      $selected = ' selected';
    }
    echo "$space  <option value=\"$report\"$selected>$report_label</option>";
  }
  echo "$space</select>";
  echo <<<EOF
      </form>
    </div>
    <div style="clear:both"></div>
  </div>
  <div style="padding: 5px 10px">
EOF;

  if ($doc_id != '') {
    include("./$doc_id.html");
  }
  else {
    $array_length = count($select_list);
    echo "<h3 style=\"padding:8px 4px 0px\">List of available documentation ($array_length)</h3><ul>";
    foreach ($select_list as $report => $report_label) {
      echo "<li><a href=\"?doc=$report\">$report_label</a></li>";
    }
    echo "</ul>";
  }

  echo <<<EOF
      </div>
    </body>
  </html>
EOF;
?>



