<?php

  /*****************************************************************
   **                                                             **
   **             ___________________________________             **
   **            |                                   |            **
   **            |  [SimonStenhouse.NET] Statistics  |            **
   **            |___________________________________|            **
   **                                                             **
   **                                                             **
   *****************************************************************/
	 
   // This is a Usage example for the Statistics script.
   // NOTE: The include must come before any output.
	 
include_once('statistics.php');
 
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<title>Simon Stenhouse - Statistics Usage Example</title>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<style type="text/css">
			* {		margin: 0px;
					padding: 0px;
					font-size: 12px;
					font-family: Verdana; }
			a {		color: #3399FF;
					text-decoration: none; }
			img {		border: 0px; }
			.title {	display: inline;
					padding: 5px 15px 5px 10px;
					font-size: 14px;
					line-height: 24px;
					font-weight: bold;
					color: #FFFFFF;
					background-color: #3399FF;
					border-bottom: 1px solid #FFFFFF;
					border-right: 1px solid #FFFFFF; }
			.subtitle {	padding: 5px 10px;
					color: #FFFFFF;
					background-color: #3399FF; }
			.subtitle a, .subtitle a:hover {
					font-size: 10px;
					color: #FFFFFF; }
			.entry {	padding: 5px;
					color: #000000;
					background-color: #F6F6F6;
					border: 1px solid #3399FF; }
			.container {	display: block;
					width: 20em; }
			.left {		float: left; }
			.right {	float: right; }
			.simon { 	font-size: 30px;
					color: #000000; }
			.stenhouse {	font-size: 30px;
					color: #3399FF; }
			#frame {	position: relative;
					margin: 0px auto;
					padding: 10px 0px;
			 		width: 21em;
					height: 100%; }
		</style>
	</head>
	<body>
		<div id="frame">
			<div><a href="http://www.simonstenhouse.net/index.php?area=projects"><span class="simon">Simon</span><span class="stenhouse">Stenhouse</span></a></div><br />
			<div class="title">Statistics Usage Example</div>
			<div class="subtitle">Displaying as Text</div>
			<div class="entry">
				<div class="container">
					<div class="left">Online:</div><div class="right"><?php echo $online; ?></div><br />
					<div class="left">Today:</div><div class="right"><?php echo $today; ?></div><br />
					<div class="left">Yesterday:</div><div class="right"><?php echo $yesterday; ?></div><br />
					<div class="left">Total:</div><div class="right"><?php echo $total; ?></div><br />
					<div class="left">IP:</div><div class="right"><?php echo $ip; ?></div><br />
				</div>
			</div>
			<div class="subtitle">Displaying as Images</div>
			<div class="entry">
				<div class="container">
					<div class="left"><img src="<?php echo $images; ?>online.gif" alt="" /></div><div class="right"><?php text_as_image($online); ?></div><br />
					<div class="left"><img src="<?php echo $images; ?>today.gif" alt="" /></div><div class="right"><?php text_as_image($today); ?></div><br />
					<div class="left"><img src="<?php echo $images; ?>yesterday.gif" alt="" /></div><div class="right"><?php text_as_image($yesterday); ?></div><br />
					<div class="left"><img src="<?php echo $images; ?>total.gif" alt="" /></div><div class="right"><?php text_as_image($total); ?></div><br />
					<div class="left"><img src="<?php echo $images; ?>ip.gif" alt="" /></div><div class="right"><?php text_as_image($ip); ?></div><br />
				</div>
			</div>
			<div class="subtitle"><a href="http://www.simonstenhouse.net/" target="_blank" title="SimonStenhouse.NET">&copy;2005 Simon Stenhouse</a></div>
		</div>
	</body>
</html>