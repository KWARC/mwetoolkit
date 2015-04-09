<?php 
echo "<br><h3>$hdr</h3>";

if (!$PHITE_vars['submitted'])
{
   echo "<font size=3><b>$spiel</b></font><br>";
   echo '<center><table border="0">';
   echo "<tr>&nbsp;<td></td><td><center><font size=2>Agree<...>Disagree</font></center></td></tr>";
   echo '<form name="quizform" action="'.$PHITE_vars['PHITE_fullcallself'].'" method="POST">';
   while (list($lineno,$datarow) = each($PHITE_listdata))
   {
         echo "<tr>";
         echo "<td align='right'><font size=2>".$datarow[0]."</font></td><td>";
         echo '<input type="radio" name="group'.$lineno.'" value="2">&nbsp';
         echo '<input type="radio" name="group'.$lineno.'" value="1">&nbsp';
         echo '<input type="radio" name="group'.$lineno.'" value="0" checked>&nbsp';
         echo '<input type="radio" name="group'.$lineno.'" value="-1">&nbsp';
         echo '<input type="radio" name="group'.$lineno.'" value="-2">&nbsp';
         echo "</td></tr>";
   }
   echo '<tr>&nbsp;<td></td><td><center><input type="submit" value="Submit"></center>';
   echo "</table></center>";
   echo '<input type="hidden" name="submitted" value="true">';
   echo '</form>';
}
else
{
   $score=0;
   while (list($lineno,$datarow) = each($PHITE_listdata))
   {
       $score+=$datarow[1]*$PHITE_vars["group$lineno"];
   }
   if ($score>0)
   {
      echo "<p><center><img src='".$PHITE_vars['PHITE_selfdir']."/$pos_pic'><br><font size=3><b><i>$pos_text</i></b></font></center><p>";
   } else
   {
      echo "<p><center><img src='".$PHITE_vars['PHITE_selfdir']."/$neg_pic'><br><font size=3><b><i>$neg_text</i></b></font></center><p>";
   }
   echo "<div align='center'><a href='".$PHITE_vars['PHITE_callself']."'>Take the test again.</a></div><p>";
   
}
?>