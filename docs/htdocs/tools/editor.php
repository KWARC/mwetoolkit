<?php
/************************************************************\
*
\************************************************************/
function template()
{
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <html>
    <head><style type="text/css">
    TD
    {
        FONT-SIZE: 12px;
        COLOR: #000000;
        FONT-FAMILY: Verdana
    }
    A:link
    {
        text-decoration: none;
        color: #2E26CD;
    }
    A:visited
    {
        text-decoration: none;
        color: #2E26CD;
    }
    A:hover
    {
        text-decoration: none;
        color: #990000;
        font-style: normal;
        background-color: transparent;
        text-decoration: underline position: relative;
        top: 1.5px;
        left: 1.5px;
    }
    </style>
    </head>
    <?php
}
extract($HTTP_GET_VARS);
extract($HTTP_POST_VARS);

//CHANGE THE LOGIN PASSWORD
//Copyright Cgixp Team
// ================================================
// SPAW PHP WYSIWYG editor control
// ================================================
// Control usage demonstration file
// ================================================
// Developed: Alan Mendelevich, alan@solmetra.lt
// Copyright: Solmetra (c)2003 All rights reserved.
// ------------------------------------------------
//                                www.solmetra.com
// ================================================
// $Revision: 1.6 $, $Date: 2004/12/30 09:38:27 $
// $Revision: 1.61 $, $Date: 2009/11/11 09:38:27 $
//    added $root_folder to edit particular location within 
//    the root folder
// ================================================

// this part determines the physical root of your website
// it's up to you how to do this
if (!ereg('/$', $HTTP_SERVER_VARS['DOCUMENT_ROOT']))
  $_root = $HTTP_SERVER_VARS['DOCUMENT_ROOT'].'';
else
  $_root = $HTTP_SERVER_VARS['DOCUMENT_ROOT'];

define('DR', $_root);
unset($_root);

// set $spaw_root variable to the physical path were control resides
// don't forget to modify other settings in config/spaw_control.config.php
// namely $spaw_dir and $spaw_base_url most likely require your modification

// you need to change the $root_folder bellow to allow editing of pages 
// within your root folder 
//$root_folder = DR.'/PT_008_Tool_Examples/PT_022_Edit_This_Page/';
include DR.'/config/editor_control.config.php';
$root_folder = DR.$editor_editfolder;
$password = $editor_password;

//$root_folder = DR.'/';
$spaw_root = DR.'/tools/spaw/';
$spaw_include = $spaw_root.'spaw_control.class.php';

//// include the control file
include $spaw_root.'spaw_control.class.php';

// here we add some styles to styles dropdown
$spaw_dropdown_data['style']['default'] = 'No styles';
$spaw_dropdown_data['style']['style1'] = 'Style no. 1';
$spaw_dropdown_data['style']['style2'] = 'Style no. 2';
?>
<?php
$action=$HTTP_GET_VARS['action'];
if ($action == "" )
{
    ?>
    <center>
    <table align=middle>
    <td align=left width=20%>
    <tr>
    <td height="27" colspan="2">
    <FONT SIZE="4" COLOR="#000000">:: Site Editor ::</FONT><br>
	
    </td>
    <tr>
    <td>Password Required</td>
    </tr>
    <tr>
    <form method=post action="?action=login">
    <td>Password:</td>
    <td><input type=password name=pass>&nbsp;
    <input type=submit value=Submit></td>
    </tr>
    </form>
    </table>
    </center>
    <?php
}

if ($action=="download")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        $filedata = stat("$dir/$p");
        $filesize = $filedata[7];
        //$ft = getfiletype("$filename");
        //header("Content-Type: $ft[1]");
        header("Content-Length: $filesize");
        header("Content-Disposition: attachment; filename=$p");
        readfile("$dir/$p");
        exit;
    }
    else
    {
        echo "Please Login";
    }
}

if ($action=="login")
{
    if ($pass==$password)
    {
        $l=base64_encode($pass);
        header("Location:?action=templates&m=$l");
    }
    else
    {
        echo "<FONT SIZE=2 COLOR=red>Invalid Password</FONT>";
    }
}

$max="9999999";
//Maximum filesize in bytes

if ($action=="view")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        template();
        echo"<center><FONT SIZE=2 face=arial>Viewing $p</FONT><table width=94% border=1 bordercolor=#AFC6DB cellspacing=0><tr><td>";
        $po=show_source("$dir/$p");
        echo "</td></tr></table><table><form method=post action=\"?action=templates&dir=$dir\"><tr><td align=middle><input type=hidden name=m value=$m><input type=submit value=Back></form></td></tr></table></center>";
    }
    else
    {
        echo "Please Login";
    }
}

if ($action=="see")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        template();
        $image_info = getimagesize("$dir/$p");
        $image_stat = stat("$dir/$p");
        echo"<center><FONT SIZE=2 face=arial>Viewing $p</FONT><table width=$image_info[0] height=$image_info[1] border=1 bordercolor=#AFC6DB cellspacing=0 valign=middle bgcolor=#fffff><tr><td align=middle valign=middle>";
        $po="<img src='$dir/$p'>";
        echo "$po</td></tr></table><table width=80% align=middle><td align=middle>$image_info[3]</td></tr></table><table><form method=post action=\"?action=templates&dir=$dir\"><tr><td align=middle><input type=hidden name=m value=$m><input type=submit value=Back></form></td></tr></table></center>";
    }
    else
    {
        echo "Please Login";
    }
}

if ($action=="changeattrib")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        template();
        echo"<form method=post action=?action=permission><FONT SIZE=2 COLOR=#00000>Change $te Permission</FONT><BR><input type=hidden name=u value='$te'><input type=hidden name=m value='$m'><input type=hidden name=path value='$dir'><input type=radio name=no value=0555>Chmod 555<BR><input type=radio name=no value=0666>Chmod 666<BR><input type=radio name=no value=0777>Chmod 777<BR><input type=submit vlaue=Change></form>";
    }
    else
    {
        echo "Please Login";
    }
}

if ($action=="permission")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        template();
        //$v=CHMOD("$path/$u",$no); 
        //$mode_dec = octdec($no);    // convert octal mode to decimal
        //chmod($filename, 0777);      
        if (!chmod($u, 0777)) {
               echo "Cannot change the mode of file ($path/$u)<BR>";
               //exit;
         };          
	echo "File Name: $u<BR>";
	echo "File Path: $path/$u<BR>";
	echo "Trying to chmod $mode_dec<BR>";
        echo "$te has been set to CHMOD $v<BR><A HREF=?action=templates&m=$m&dir=$path>Back</A>";
    }
    else
    {
        echo "Please Login";
    }
}

if ($action=="tempedit")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        template();
        $te=$HTTP_GET_VARS['te'];
        $dir=$HTTP_GET_VARS['dir'];
        $filename = "$dir/$te";
        $fd = fopen ($filename, "r");
        $stuff = fread ($fd, filesize ($filename));
        fclose ($fd);
        ?>
        <td height="399" bgcolor="" width="81%" valign="top">
        <center>
        <form method="post" action="?action=temp2&dir=<?php echo $dir ?>&te=<?php echo $te ?>">
        <table width="100%" border="1" bgcolor="D6D5D4" bordercolor="#778899" cellpadding="0" cellspacing="0">
        <tr>
        <td>
            <font size="1">File editor editing <?php echo $filename; ?></font><br>
        </td>
        </tr>
        <tr>
        <td width="86%" align=middle>
        <?php
            $sw = new SPAW_Wysiwyg('spaw1' /*name*/, $stuff /*value*/);
            $sw->show();
        ?>
        </td>
        </tr>
        <tr>
        <td width="86%" align=middle>
        <input type=hidden name=m value=<?php echo $m;?>>&nbsp;
        <input type="submit" name="Submit" value="Save">&nbsp;
        <input type="button" name="Cancel" value="Cancel" onclick="javascript: history.back(1)">
        </td>
        </tr>
        <tr>
        </tr>
        </table></center>
        </form>
        <?php
    }
    else
    {
        echo "Please Login";
    }
}

if ($action=="temp2")
{
    $n=base64_decode($m);
    if ($n==$password)
    {
        template();
        $cont=stripslashes($spaw1);
        $fil = "$dir/$te";
        $fp = fopen($fil, "w");
        fputs($fp, $cont);
        fclose($fp);
        ?>
        <td height="399" bgcolor="<?php echo $color1 ?>" width="81%" valign="top">
        <table width="100%" border="0" cellpadding="5" cellspacing="0">
        <tr>
        <td align=middle><font size="2">File saved<BR>
            <?php echo "<a href='?action=templates&dir=$dir&m=$m'>Go Back</a>";?></font><br>
        </td>
        </tr>
        </table>
        <?php
    }
    else
    {
        echo"Please Login";
    }
}

if ($action=="templates")
{
    $n=base64_decode($m);
    if($n==$password)
    {
        template();
        ?>
        <td height="399" bgcolor="<?php echo $color1 ?>" width="81%" valign="top">
        <table width="100%" border="0" cellpadding="5" cellspacing="0">
        
<tr><td><font size="1"><?php //echo "Dir:<br>";	echo "$dir";?></font></td></tr>

	<tr><td><font size="1"></font></td></tr>
        <tr valign="top"></td>
        </tr>
        <tr>
        <td width="86%">
        <?php
        if ($dir=="")
        {
            //$dir=DR;
            $dir=$root_folder;
        }
        if ($do=="delete")
        {
            $fd = unlink("$dir/$te");
            echo "<center>File has been deleted<BR>";
        }
        if($do=="doupload")
        {
          
	$uploaddir = $dir;
	$uploadfile = $uploaddir . "/" . basename($_FILES['fileupload']['name']);
//echo "DR: " . DR . "<br>";
//echo "$root_folder: " . $root_folder . "<br>";
//echo "Upload Dir: $uploaddir <br>";
//echo "Upload File: $uploadfile <br>";
//echo "FileName: " . $_FILES['fileupload']['tmp_name'] . " <br>";
//print_r($_FILES);
//echo " <br>";

	echo '<pre>';

		if (move_uploaded_file($_FILES['fileupload']['tmp_name'], $uploadfile)) {
   			echo "File is valid, and was successfully uploaded.\n";
		} else {
   			echo "Possible file upload attack!\n";
		}

	print "</pre>";
  
          
        }

	echo"<table align=center BORDER=\"1\" CELLSPACING=\"1\" CELLPADDING=\"0\" align=middle bordercolor=#AFC6DB><td><form  ENCTYPE=multipart/form-data method=post action=?action=templates&do=doupload&m=$m>Upload: <input type=file name=fileupload><input type=hidden name=dir value=$dir><input type=hidden name=m value=$m><input type=submit value=Upload></form> </td></table>";
        echo "<center><TABLE WIDTH=\"85%\" BORDER=\"1\" CELLSPACING=\"1\" CELLPADDING=\"0\" align=middle bordercolor=#AFC6DB><TR><td></td><TD COLSPAN=\"2\" BGCOLOR=\"#ffffff\" width=55%><FONT COLOR=\"#000000\" SIZE=\"-1\" FACE=\"Verdana\">Filename</td><td width=5% align=center>Edit</td><td width=10% align=middle>Filesize</td><td width=10% align=middle>Permission</td><td width=10% align=middle>Download</td><td align=middle>Delete</td></FONT></TR>";
	
        $handle = @opendir($dir);
        while (false !== ($file = readdir($handle)))
        {
            $attrib=fileperms("$dir/$file");
            $filesize=filesize("$dir/$file");
            $file_size_now = round($filesize / 1024 * 100) / 100 . "Kb";
            $n= explode(".",$file);
            $show = 0;
            if ($n[1] == "")
            {
                $show = 1;
                $img="./images/dir.gif";
            }
            elseif($n[1]=="inc")
            {
                $show = 1;
                $img="./images/txt.gif";
            }
            elseif($n[1]=="tpl")
            {
                $show = 1;
                $img="./images/txt.gif";
            }
            elseif($n[1]=="php")
            {
                $show = 0;
		$img="./images/php.jpg";
            }
            elseif($n[1]=="zip")
            {
                $img="./images/zip.gif";
            }
            elseif($n[1]=="gif")
            {
		$show = 1;
                $img="./images/gif.gif";
            }
            elseif($n[1]=="html")
            {
		$show = 1;
                $img="./images/html.gif";
            }
            elseif($n[1]=="ini")
            {
                $show = 1;
		$img="./images/ini.gif";
            }
            elseif($n[1]=="jpg")
            {
		$show = 1;
                $img="./images/jpg.gif";
            }
            elseif($n[1]=="txt")
            {
                $show = 1;
                $img="./images/txt.gif";
            }
            elseif($n[1]=="exe")
            {
                $img="./images/exe.gif";
            }
            else
            {
                $img="./images/no.gif";
            }
            if ($n[1] == "")
            {
                $link="?action=templates&m=$m&dir=$dir/$file";
                $link1="-";
            }
            elseif ($n[1] == "gif")
            {
                $link="?action=see&m=$m&p=$file&dir=$dir";
                $link1="-";
            }
            elseif ($n[1] == "jpg")
            {
                $link="?action=see&m=$m&p=$file&dir=$dir";
                $link1="-";
            }
            elseif ($n[1] == "zip")
            {
                $link="?action=download&m=$m&p=$file&dir=$dir";
                $link1="-";
            }
            elseif ($n[1] == "exe")
            {
                $link="?action=download&m=$m&p=$file&dir=$dir";
                $link1="-";
            }
            else
            {
                $link="?action=view&p=$file&dir=$dir&m=$m";
                $link1="<a href='?action=tempedit&m=$m&te=$file&dir=$dir'>Edit</a>";
            }
            if($dir!=".")
            {
                $uplink="<tr><td></td><td align=middle><a href='?action=templates&m=$m'><img src=./images/up.gif border=0>Home</a></td></tr></table></center>";
            }
            else
            {
                $uplink="</table>";
            }
            if ($file != "." && $file != ".." &&  $file != "editor.php" && $show == 1 )
            {
                echo "<TR><TD align=middle><IMG SRC=\"$img\"  BORDER=0 ></td><TD COLSPAN=\"2\" BGCOLOR=\"#ffffff\" width=30%>&nbsp;
                <FONT COLOR=\"#000000\" SIZE=\"-1\" FACE=\"Verdana\"><a href=\"$link\">$file</a></td><td width=10% align=middle>$link1</td><td width=10% align=middle>$file_size_now</td><td width=10% align=middle><a href='?action=changeattrib&m=$m&te=$file&dir=$dir'>$attrib</a></td><td align=middle><a href='?action=download&m=$m&p=$file&dir=$dir'>Download</a></td><td align=middle><a href=\"?action=templates&do=delete&m=$m&te=$file&dir=$dir\" alt=Delete><img src=\"./images/del.gif\" border=0></img></a></td></FONT></TR>";
            }
        }
        echo "</table><table><BR>$uplink";
        closedir($handle);
        ?>
        </td>
        </tr>
        </table>
        </form>
        <?php
    }
    else
    {
        echo "Please Login Again";
    }
}
echo "<BR><CENTER><FONT SIZE=2 face=arial>Powered By <A HREF=http://www.phite.org.au target=_new>Site Editor</A></font></CENTER>";
?> 
