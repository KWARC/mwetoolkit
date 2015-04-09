function popup(mylink, windowname, win_width, win_height)
{
if (! window.focus)return true;
var href;

if (typeof(mylink) == 'string')
   href=mylink;
else
   href=mylink.href;

window.open(href, windowname, 'width='+win_width+',height='+win_height+',scrollbars=yes');

return false;
}