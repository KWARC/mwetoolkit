<?php 
echo "<br><center><h3>$hdr</h3>";
if ($img <> "") echo '<img src="'.$PHITE_vars['PHITE_selfdir'].'/'.$img.'"><p>';
echo "<table width=95% border='0'><font size=2>$spiel</font></table></center><p>";

echo "<center><table width=95% bgcolor=$col0 cellpadding=0 cellspacing=1>";
while (list($lineno,$datarow) = each($PHITE_listdata))
{
     echo "<tr><td><table width=100% cellspacing=0>";
     echo "<tr bgcolor=$col1>";
     echo "<td align='left'><font size=2><b>".$datarow[0]."</b></font>";
     echo "</td></tr>";
     echo "<tr bgcolor=$col2>";
     echo "<td align='left'><font size=2>".$datarow[1]."</font>";
     echo "</td></tr></table></td></tr>";
}
echo "</table></center>";
?>