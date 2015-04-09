<?php
// FORM TO EMAIL
// http://www.webformdesigner.com
// The following variables can be changed to suit

// this part determines the physical root of your website
// it's up to you how to do this
if (!ereg('/$', $HTTP_SERVER_VARS['DOCUMENT_ROOT']))
  $_root = $HTTP_SERVER_VARS['DOCUMENT_ROOT'].'';
else
  $_root = $HTTP_SERVER_VARS['DOCUMENT_ROOT'];
define('DR', $_root);
unset($_root);
include DR.'/config/mailer_control.config.php';

// Change this to the email address where the message is to be sent
//$your_email = "someone@domain.com.au";
$your_email = $mailer_toAddress;

// This is what is displayed in the email subject line
// Change it if you want
$subject = $mailer_subject;

// This is the return URL after the form has been processed
//$thankyou = "thankyou_page.html";
$thankyou = $mailer_thankyou;

// You shouldn't need to edit below this line
// ---------------------------------------------
$name = trim(stripslashes($_POST['name']));
$email = trim(stripslashes($_POST['email']));

$year = date("Y");
$month = date("m");
$day = date("d");
$hour = date("h");
$min = date("i");
$tod = date("a");


  // This section checks the referring URL to make sure it's all coming
    // from our own site
    // Get the referring URL
    $referer = $_SERVER['HTTP_REFERER'];
    $referer_array = parse_url($referer);
    $referer = strtolower($referer_array['host']);

    // Get the URL of this page
    $this_url = strtolower($_SERVER['HTTP_HOST']);

    // If the referring URL and the URL of this page don't match then
    // display a message and don't do download or send the email.
    if ($referer != $this_url) {
        echo "ERROR: You do not have permission to use this script from another URL. \n";
        echo "Referer: " .$referer . "\n";
        echo "This URL: " .$this_url. "\n";
        exit;
    }

    // Timestamp this message
    $TimeOfMessage = date('d')."/".date('m')."/".date('y')."(".date('D').") @ ".date('H:i');

    // finally, send e-mail
    $ip=$_SERVER["REMOTE_ADDR"];
    $message = "The following was sent on " .$TimeOfMessage."\n";
    $message .= "---------------------------------------------------------\n";

    // send the complete set of variables as well
    while (@list($var,$val) = @each($_POST)) {
      $message .= "$var: $val\n";
	}

    // send the email
    mail($your_email, $subject, $message, "From: $name <$email>");

    // go to return URL
    if (isset($thankyou)) {
	header("Location: $thankyou");
	exit();
    }



?>