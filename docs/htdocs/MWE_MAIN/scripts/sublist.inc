<?php
# Small script to list next level of directories as an
# unordered list of links.
# Call by adding PHITE_script('sublist');
# CJR 1/12/03
#
  $sitesig=$PHITE_vars['sitesig'];
  $
  $dirs = getlist(".",$sitesig,"dir");
  if ($dirs) while($entry=each($dirs))
  {
      $filename=$entry['key'];
	  $text=$entry['value'];
      if (strtolower($filename)==strtolower($sitesig."_MAIN")) continue; # Do not show MAIN directory
	  $redir =filestarting("./".$filename,"redirect",'inc');
	  if ($redir=="")
	  {
	    $link = $siteroot."/".basename($PHP_SELF)."?sitesig=".$sitesig."&page=".str_replace(' ','%20',$filename);
	  }else {  
	  	$link=buf_out('./'.str_replace(' ','%20',$filename).'/'.$redir); #get redirected output
	  }

      $tpl->newBlock("LEFT_NAV");
      $tpl->assign("OPTION_LINK",$link);
      $tpl->assign("OPTION_NAME",$text);
	  
	  # If this is current directory (or $alwaysshowsubs is set) check for subdirs  
	  if ($alwaysshowsubs || strtolower($filename)==strtolower($page))
	  {
	    $subdirs = getlist("./".$filename,$sitesig,"dir");
        if ($subdirs) while($subentry=each($subdirs))
        {
          $subfilename=$subentry['key'];
	      $subtext=$subentry['value'];
	      $redir =filestarting("./".$filename."/".$subfilename,"redirect",'inc');
	      if ($redir=="")
	      {
	        $sublink = $siteroot."/".basename($PHP_SELF)."?sitesig=".$sitesig."&page=".str_replace(' ','%20',$filename)."&subpage=".str_replace(' ','%20',$subfilename);
	      }else {
	  	    $sublink=buf_out('./'.str_replace(' ','%20',$filename).'/'.str_replace(' ','%20',$subfilename).'/'.$redir); #get redirected output
	      }

          $tpl->newBlock("SUB_NAV");
          $tpl->assign("SUB_LINK",$sublink);
          $tpl->assign("SUB_NAME",$subtext);
		}
	  }
  }
