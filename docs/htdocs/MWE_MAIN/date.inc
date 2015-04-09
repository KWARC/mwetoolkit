<?php 
$today = getdate(); 
$month = $today['month']; 
$mday = $today['mday']; 
$year = $today['year']; 
echo "$month $mday, $year";
?>