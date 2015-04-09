<?php 
echo '<h3>Test Script file</h3>';
$today = getdate(); 
$month = $today['month']; 
$mday = $today['mday']; 
$year = $today['year']; 
echo "$month $mday, $year <br>";
echo 'Teddy ='.$teddy.'<p>';
echo '<table border="1">';

while (list($lineno,$datarow) = each($PHITE_listdata))
{
  echo "<tr><td>$lineno</td>";
   while (list($no,$item)=each($datarow))
   {
       echo "<td>$item</td>";
   }
   echo "</tr>";
}
echo "</table>";
?>