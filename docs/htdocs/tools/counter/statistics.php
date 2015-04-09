<?php

  /*****************************************************************
   **                                                             **
   **             ___________________________________             **
   **            |                                   |            **
   **            |  [SimonStenhouse.NET] Statistics  |            **
   **            |___________________________________|            **
   **                                                             **
   **                                                             **
   **  ---------------------------------------------------------  **
   **                                                             **
   **  Author:  Simon Stenhouse                                   **
   **  Date:    01.11.2006                                        **
   **  Version: 1.2                                               **
   **  Website: http://www.simonstenhouse.net/                    **
   **  License: http://www.gnu.org/licenses/gpl.txt               **
   **                                                             **
   **  ---------------------------------------------------------  **
   **                                                             **
   **  Requirements:                                              **
   **                                                             **
   **   - PHP 4 >= 4.3.0 or PHP 5                                 **
   **                                                             **
   **  Features:                                                  **
   **                                                             **
   **   - Easy Installation                                       **
   **   - Flat file system (no database needed)                   **
   **   - Display visitor data as text or images                  **
   **   - Show the number of users currently online               **
   **   - Show unique IP counts for Today, Yesterday and Total    **
   **   - Optional email notification upon reaching milestones    **
   **   - Administration Area for viewing/editing statistics      **
   **                                                             **
   **  ---------------------------------------------------------  **
   **                                                             **
   **  Installation:                                              **
   **                                                             **
   **   1 Open statistics.php and adjust the settings in the      **
   **     configuration area as needed.                           **
   **                                                             **
   **   2 Upload statistics.php to your sites root directory.     **
   **                                                             **
   **   3 Create a directory named 'data' off of the root         **
   **     and then CHMOD 777 that directory.                      **
   **                                                             **
   **   4 Create a directory named 'images' off of the root       **
   **     and then upload the included image files to it.         **
   **                                                             **
   **  ---------------------------------------------------------  **
   **                                                             **
   **  Resulting Structure:                                       **
   **                                                             **
   **   /statistics.php                                           **
   **   /data/                                                    **
   **   /images/0.gif                                             **
   **   /images/1.gif                                             **
   **   /images/2.gif                                             **
   **   /images/3.gif                                             **
   **   /images/4.gif                                             **
   **   /images/5.gif                                             **
   **   /images/6.gif                                             **
   **   /images/7.gif                                             **
   **   /images/8.gif                                             **
   **   /images/9.gif                                             **
   **   /images/dot.gif                                           **
   **   /images/comma.gif                                         **
   **   /images/online.gif                                        **
   **   /images/today.gif                                         **
   **   /images/yesterday.gif                                     **
   **   /images/total.gif                                         **
   **   /images/ip.gif                                            **
   **                                                             **
   **  ---------------------------------------------------------  **
   **                                                             **
   **  Usage example:                                             **
   **                                                             **
   **   Online: <?php echo $online; ?>                            **
   **   Today: <?php echo $today; ?>                              **
   **   Yesterday: <?php echo $yesterday; ?>                      **
   **   Total: <?php echo $total; ?>                              **
   **                                                             **
   **   Online: <?php text_to_image($online); ?>                  **
   **   Today: <?php text_to_image($today); ?>                    **
   **   Yesterday: <?php text_to_image($yesterday); ?>            **
   **   Total: <?php text_to_image($total); ?>                    **
   **                                                             **
   **   See the included 'example.php' file for a more detailed   **
   **   example.                                                  **
   **                                                             **
   **  ---------------------------------------------------------  **
   **                                                             **
   **  History:                                                   **
   **                                                             **
   **   1.2 - 01.11.2006                                          **
   **                                                             **
   **         Fixed: Total Count Reset Bug                        **
   **                                                             **
   **          When the script is executed too many times, at the **
   **          same time, the total.dat file would become corrupt **
   **          and revert to zero.                                **
   **                                                             **
   **          Fix involved padding the total.dat file so its     **
   **          filesize (in bytes) would give the total count.    **
   **                                                             **
   **         Added: Administration Area                          **
   **                                                             **
   **          When the statistics.php page is viewed directly,   **
   **          the owner(s) can login to view the statistics      **
   **          and edit the total count if needed.                **
   **                                                             **
   **          Please be aware that your total count is the same  **
   **          as the filesize of your total.dat file (in bytes). **
   **                                                             **
   **          For example, if your total count was 1048576, your **
   **          total.dat file would be 1 megabyte in size.        **
   **                                                             **
   **   1.1 - 03.01.2006                                          **
   **                                                             **
   **         Fixed: Visitor Count                                **
   **                                                             **
   **          Visitor counts are tracked by IP addresses. IP's   **
   **          visiting Today, that had also visited Yesterday,   **
   **          had their Yesterday record updated to Today. This  **
   **          was correct but their visit for Yesterday was then **
   **          lost and not included in the Yesterday count.      **
   **                                                             **
   **          To rectify this, the system for incrementating     **
   **          counts has been changed so an IP can now have a    **
   **          record for both Today and Yesterday.               **
   **                                                             **
   **   1.0 - 22.11.2005                                          **
   **                                                             **
   **         Full Release with all features present.             **
   **                                                             **
   *****************************************************************/




  /*****************************************************************
   **                                                             **
   **                  C O N F I G U R A T I O N                  **
   **                                                             **
   *****************************************************************/


// PATHS
// -----------------------------------------------------------------

// Root path of your site
$root = $_SERVER['DOCUMENT_ROOT'] . '/tools/counter/';

// Path to image files
$images = 'images/';

// Path to data files
// NOTE: This directory must have been CHMOD'd to 777
$data = 'data/';


// ADMIN USERS
// -----------------------------------------------------------------

// Admin accounts, in the format of "username" => "password"
// NOTE: For security reasons, you should change all of these
$users = array( "tombr" => "casper" );


// NUMBER FORMATTING
// -----------------------------------------------------------------

// Set to true if you want your numbers to be formatted with comma's (",") (true or false)
// EXAMPLE: If this is set to true, the number 10123 will be displayed as 10,123.
$use_number_format = true;


// EMAIL NOTIFICATION
// -----------------------------------------------------------------

// Set to true if you want to receive an email notification whenever your total visitor count reaches a milestone (true or false)
$notify = true;

// Your email
$email = 'tombr@samsa.com.au';

// Your site address
$domain = 'www.rangeschessclub.com.au';

// Total visitor counts that are regarded as milestones
$milestones = array(1, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 7500, 10000, 25000, 50000, 75000, 100000, 250000, 500000, 750000, 1000000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000, 4500000, 5000000, 10000000);




  /*****************************************************************
   **                                                             **
   **                      F U N C T I O N S                      **
   **                                                             **
   *****************************************************************/


// PURPOSE:	Check whether a file exists.  If it doesn't, the file is created.
// PARAMS:	[string] $file - The full path and name of a file
// RETURN:	[bool] True if file exists | False if file didn't exist but was created
function statistics_check_file($file)
{
	if (!file_exists($file))
	{
		$handle = fopen($file, "w");
		fclose($handle);
		chmod($file, 0666);
		
		return false;
	}
	
	return true;
}


// PURPOSE:	Converts a number string to an image representation.
// PARAMS:	[string] $number - A number, in the format of #### or #,###
// RETURN:	[echo] XHTML image tags
function text_as_image($number)
{
	global $images;
	
	for ($i = 0; $i < strlen($number); $i++)
	{
		$digit = substr($number, $i, 1);
		
		if ($digit == ".")
		{
			$digit = "dot";
		}
		elseif ($digit == ",")
		{
			$digit = "comma";
		}
		
		echo '<img src="' . $images . $digit . '.gif" alt="" />';
	}
}


// PURPOSE:	Displays the header
// RETURN:	[echo] XHTML
function display_header()
{
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<title>Simon Stenhouse - Statistics</title>
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
			.simon {	font-size: 30px;
					color: #000000; }
			.stenhouse {	font-size: 30px;
					color: #3399FF; }
			.form_button {	height: 27px;
					font-size: 14px;
					font-weight: bold;
					border-width: 0px;
					color: #FFFFFF;
					background-color: #3399FF; }
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
			<div class="title">Statistics Administration</div>
<?php
}


// PURPOSE:	Displays the login
// RETURN:	[echo] XHTML
function display_login()
{
?>
			<div class="subtitle">&nbsp;</div>
			<div class="entry">
			<form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">
				<div class="container">
					Username:<br />
					<input type="text" name="username" size="32" value="" /><br /><br />
					Password:<br />
					<input type="password" name="password" size="32" value="" /><br /><br />
					<input type="hidden" name="login" value="1" />
				</div>
			</div>
			<div align="right">
				<input type="submit" name="submit" value="Login" class="form_button" />
			</div>
			</form>

			<br />
<?php
}


// PURPOSE:	Displays success or failure messages
// RETURN:	[echo] XHTML
function display_message()
{
        global $message;

        if ($message != null)
        {
        ?>
			<div class="subtitle">Message</div>
			<div class="entry">
				<div class="container">
					<?php echo $message; ?>
				</div>
			</div>

			<br />
        <?php
        }
}


// PURPOSE:	Displays the statistics
// RETURN:	[echo] XHTML
function display_statistics()
{
        global $online, $today, $yesterday, $total, $ip;

        ?>
			<div class="subtitle">Statistics</div>
			<div class="entry">
				<div class="container">
					<div class="left">Online:</div><div class="right"><?php echo $online; ?></div><br />
					<div class="left">Today:</div><div class="right"><?php echo $today; ?></div><br />
					<div class="left">Yesterday:</div><div class="right"><?php echo $yesterday; ?></div><br />
					<div class="left">Total:</div><div class="right"><?php echo $total; ?></div><br />
					<div class="left">IP:</div><div class="right"><?php echo $ip; ?></div><br />
				</div>
			</div>
	<?php
}


// PURPOSE:	Displays a form for editing the total count
// RETURN:	[echo] XHTML
function display_edit()
{
        global $total;

        ?>
			<div class="subtitle">Total</div>
			<div class="entry">
			<form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>" enctype="multipart/form-data">
				<div class="container">
					<input type="text" name="count" size="32" value="<?php echo $total; ?>" /><br /><br />
					<input type="hidden" name="edit" value="1" />
					<input type="hidden" name="username" value="<?php echo $_POST['username']; ?>" />
					<input type="hidden" name="password" value="<?php echo $_POST['password']; ?>" />
				</div>
			</div>
			<div align="right">
				<input type="submit" name="submit" value="Edit" class="form_button" />
			</div>
			</form>

			<br />

			<div class="subtitle">Note</div>
			<div class="entry">
				Please be aware that your total count is the same as the filesize of your total.dat file (in bytes).
				<br /><br />
				For example, if your total count was 1048576, your total.dat file would be 1 megabyte in size.
			</div>

			<br />
        <?php
}


// PURPOSE:	Displays the logout
// RETURN:	[echo] XHTML
function display_logout()
{
        global $total;
        ?>
			<div class="subtitle">&nbsp;</div>
			<div class="entry">
				<div class="container" align="center">
					<a href="statistics.php?logout">LOGOUT</a>
				</div>
			</div>
        <?php
}

// PURPOSE:	Displays the footer
// RETURN:	[echo] XHTML
function display_footer()
{
?>
			<div class="subtitle"><a href="http://www.simonstenhouse.net/" target="_blank" title="SimonStenhouse.NET">&copy;2006 Simon Stenhouse</a></div>
		</div>
	</body>
</html>
<?php
}




  /*****************************************************************
   **                                                             **
   **           I N I T I A L I S E   V A R I A B L E S           **
   **                                                             **
   *****************************************************************/

// DATA FILES
$file_detail   = $root . $data . 'detail.dat';
$file_total    = $root . $data . 'total.dat';
$file_notify   = $root . $data . 'notify.dat';

// VARIABLES
$query         = $_SERVER['QUERY_STRING'];
$ip            = $_SERVER['REMOTE_ADDR'];
$online        = 0;
$today         = 0;
$yesterday     = 0;
$total         = '';

$minutes       = 15;
$time          = time();
$day           = date("j");
$month         = date("n");
$year          = date("Y");

$detail        = '';
$match         = false;
$match_today   = false;
$milestone_new = false;




  /*****************************************************************
   **                                                             **
   **                         S C R I P T                         **
   **                                                             **
   *****************************************************************/


// If the detail file doesn't exist, it will be created
statistics_check_file($file_detail);

// Read data from detail file into an array
$detail = explode("\n", file_get_contents($file_detail));

// Open the detail file for modification
$handle_detail = fopen($file_detail, "w");

// Loop through the detail array
foreach ($detail as $line)
{
	// Split and store array values
	list($stored_ip, $stored_time, $stored_day, $stored_month, $stored_year) = explode("|", $line);

	// Determine yesterday's correct date
	$temp_day = $day - 1;
	$temp_month = $month;
	$temp_year = $year;

	if ($temp_day == 0)
	{
		$temp_month--;
		if ($temp_month == 0)
		{
			$temp_month = 12;
			$temp_year--;
		}
		switch ($temp_month)
		{
			case 1: 	$temp_day = 31; break;
			case 2: 	$temp_day = 28; break;
			case 3: 	$temp_day = 31; break;
			case 4: 	$temp_day = 30; break;
			case 5: 	$temp_day = 31; break;
			case 6: 	$temp_day = 30; break;
			case 7: 	$temp_day = 31; break;
			case 8: 	$temp_day = 31; break;
			case 9: 	$temp_day = 30; break;
			case 10:	$temp_day = 31; break;
			case 11:	$temp_day = 30; break;
			case 12:	$temp_day = 31; break;
		}
	}

	// If the users ip matches a stored ip...
	if ($stored_ip == $ip)
	{
		$match = true;

		// And the user is already visited today...
		if ($stored_day == $day && $stored_month == $month && $stored_year == $year)
		{
			$match_today = true;

			// Update time of visit
			$stored_time = $time;
		}
	}

	// If stored visit was today...
	if ($stored_day == $day && $stored_month == $month && $stored_year == $year)
	{
		// Write back into detail file
		fwrite($handle_detail, "$stored_ip|$stored_time|$stored_day|$stored_month|$stored_year\n");

		// Increment the Today count
		$today++;

		// If the user was online within the last 15 minutes...
		if ($time < $stored_time + ($minutes * 60))
		{
			// Increment the Online count
			$online++;
		}
	}
	// If stored visit was yesterday...
	elseif ($stored_day == $temp_day && $stored_month == $temp_month && $stored_year == $temp_year)
	{
		// Write back into detail file
		fwrite($handle_detail, "$stored_ip|$stored_time|$stored_day|$stored_month|$stored_year\n");

		// Increment the Yesterday count
		$yesterday++;
	}
}

// If the user is not recorded as having visited OR if the user is recorded as having visited yesterday but not today...
if (!$match || $match && !$match_today)
{
	// Write todays visit into detail file
	fwrite($handle_detail, "$ip|$time|$day|$month|$year\n");

	// Increment the Online and Today count
	$online++;
	$today++;

	// Pad the total count
	$total = '.';
}

// Close the detail file
fclose ($handle_detail);

// If the total file doesn't exist, it will be created
statistics_check_file($file_total);

// If the total was padded, pad the total file
if ($total != '')
{
	$handle_total = fopen($file_total, "a");
	flock($handle_total, LOCK_EX);
	fwrite($handle_total, $total);
	fclose($handle_total);
}

// Get current total count from total file
$total = strlen(file_get_contents($file_total));

// If the notify file doesn't exist, it will be created and the default value of 0 will be written into it
if (!statistics_check_file($file_notify))
{
	$handle_notify = fopen($file_notify, "w");
	flock($handle_notify, LOCK_EX);
	fwrite($handle_notify, "0");
	fclose($handle_notify);
}

// Read data from notify file (the last milestone reached)
$milestone_last = file_get_contents($file_notify);

// Open the notify file for modification
$handle_notify = fopen($file_notify, "w");
flock($handle_notify, LOCK_EX);

// Loop through the milestones array
foreach ($milestones as $milestone)
{
	// If total count is a milestone, and this milestone hasn't already been reached,...
	if ($total == $milestone && $milestone_last < $total)
	{
		// Write latest milestone into notify file
		fwrite($handle_notify, $total);
		$milestone_new = true;
		break;
	}
}

// If a new milestone was not recorded, write the old milestone back into the notify file
if (!$milestone_new)
{
	fwrite($handle_notify, $milestone_last);
}

// Close the notify file
fclose($handle_notify);

// If email notification is turned on and a new milestone was reached, email the user
if ($notify && $milestone_new)
{
	$mail_date = date ("d F Y");
	$mail_time = date ("g:i A");
	$mail_subject = "[ $domain ] Statistics - $total";
	$mail_to = "$email";
	$mail_message = "SITE:                $domain\nDATE:                $mail_date, $mail_time\nMILESTONE:           $total\n";
	$mail_headers = "From:	$mail_subject <$mail_to>\n";
	$mail_sent = mail($mail_to, $mail_subject, $mail_message, $mail_headers);
}

// If number formatting is turned on, apply the formatting
if ($use_number_format)
{
	$online = number_format($online);
	$today = number_format($today);
	$yesterday = number_format($yesterday);
	$total = number_format($total);
}


// AUTHENTICATION FOR ADMIN AREA
// -----------------------------------------------------------------

// Check to see if the user is at the statistics page
if (basename($_SERVER['PHP_SELF']) == 'statistics.php')
{
	if ($query == 'logout')
	{
		$message = "You have successfully logged out.<br /><br />It is strongly recommended that you now close this browser/tab.";
		display_header();
		display_message();
		die(display_footer());
	}
	elseif (empty($_POST['username']) || empty($_POST['password']))
	{
		$message = "You must enter a valid username and password to access this area.";
		display_header();
		display_message();
		display_login();
		die(display_footer());
	}
	elseif (strcmp($users[$_POST['username']], $_POST['password']) == 0)
	{
		// ADMIN AREA
		// -------------------------------------------------

		if ($_POST['edit'])
		{
			// If the user supplied value is an integer...
			if (is_int(abs($_POST['count'])))
			{
				$total = abs($_POST['count']);

				// Truncate the total file and pad it to the new value
				$handle_total = fopen($file_total, "w");
				flock($handle_total, LOCK_EX);
				for ($i = 0; $i < $total; $i++)
				{
					fwrite($handle_total, '.');
				}
				fclose($handle_total);

				$message = "You have successfully changed the total to " . $total . ".";
				display_header();
				display_message();
				display_statistics();
				display_edit();
				display_logout();
				die(display_footer());
			}
			else
			{
				$message = "You must enter a number (integer).";
				display_header();
				display_message();
				display_statistics();
				display_edit();
				display_logout();
				die(display_footer());
			}
		}
		else
		{
			display_header();
			display_statistics();
			display_edit();
			display_logout();
			die(display_footer());
		}
	}
	else
	{
		$message = "You must enter a valid username and password to access this area.";
		display_header();
		display_message();
		display_login();
		die(display_footer());
	}
}
?>
