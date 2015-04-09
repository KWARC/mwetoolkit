<?php 
global $PHITE_vars;
if (!strstr($PHITE_vars['PHITE_fullcallself'],'?')) $c='?';
else $c='&';
$pf=$PHITE_vars['PHITE_fullcallself'].$c.'skin=_PrintFriendly';
print("<a href=\"$pf\" target=\"_blank\">Printer Friendly Page</a>");
?>