   *****************************************************************
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
   *****************************************************************