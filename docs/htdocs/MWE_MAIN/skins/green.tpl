<html>
<head>
<title>{PAGETITLE}</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body bgcolor="#009966" text="#000000" link="#009966" vlink="#006633" alink="#CCCCCC" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0">
<table width="100%" border="0" cellspacing="0" cellpadding="5" height="70" bgcolor="#009966">
  <tr>
    <!--<td align="center" valign="middle">logo</td>--> 
	<td align="left" valign="middle"><i><b><font face="Arial, Helvetica, sans-serif" color="#FFFFFF" size="5">
	{SITENAME}: {PAGETITLE}
	</font></b></i></td>
  </tr>
</table>

<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr align="left" valign="top"> 
	<td width="140" height="400" bgcolor="#ECECEC"> <b><font face="Arial, Helvetica, sans-serif" size="2">
	<br><a href="{HOMELINK}">{HOMENAME}</a><br><br>
<!-- START BLOCK : LEFT_NAV -->
      <b><font face="Arial, Helvetica, sans-serif" size="2">
	  &gt; <a href="{OPTION_LINK}">{OPTION_NAME}</a><br></font></b>
<!-- START BLOCK : SUB_NAV -->
      <font face="Arial, Helvetica, sans-serif" size="1">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#149;	
	  <a href="{SUB_LINK}">{SUB_NAME}</a><br></font>
<!-- END BLOCK : SUB_NAV -->
<!-- END BLOCK : LEFT_NAV -->
      <br>		  
      <br>	
<!-- START BLOCK : LEFT_BOX -->	  
	  <table width="90%" border="1" cellspacing="0" cellpadding="2" align="center">
		<tr><td bgcolor="#33CC99" align="center" valign="top"><font color="#FFFFFF" size="1" face="Arial, Helvetica, sans-serif"> 
			{LB_TITLE}</font></td></tr>
		<tr><td><font face="Arial, Helvetica, sans-serif" size="1">{LB_CONTENT}</font></tr>
	  </table><br>
<!-- END BLOCK : LEFT_BOX -->
	  <br>
	</td>
	<td bgcolor="#FFFFFF"> 
  
{BODY}

<!-- START BLOCK : CENTER_BOX -->
<p><hr><br><b>{CENTER_TITLE}</b><br>
{CENTER_CONTENT}
<!-- END BLOCK : CENTER_BOX -->

	</td>
	<td width="200" bgcolor="#FFFFFF"> 
<!-- START BLOCK : RIGHT_BOX -->
	  <table width="200" border="0" cellspacing="0" cellpadding="1">
		<tr> 
		  <td bgcolor="#009966" align="center" valign="top"><b><font color="#FFFFFF" size="2" face="Arial, Helvetica, sans-serif"> 
			{RB_TITLE}</font> </b> 
			<table width="100%" border="0" cellspacing="0" cellpadding="3">
			  <tr> 
				<td bgcolor="#FFFFFF"> 
                  {RB_CONTENT}
				</td>
			  </tr>
			</table>
		  </td>
		</tr>
	  </table><br>
<!-- END BLOCK : RIGHT_BOX -->
	</td>
  </tr>
</table>
<table width="100%" border="0" cellspacing="0" cellpadding="5">
  <tr bgcolor="#009966"> 
	<td width="110">&nbsp;</td>
	<td align="center" valign="middle"><font color="#FFFFFF" size="1" face="Arial, Helvetica, sans-serif">
	{FOOTER}</font></td>
	<td width="200">&nbsp;</td>
  </tr>
</table>
</body>
</html>
