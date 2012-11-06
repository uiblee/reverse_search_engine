


// the script below will pull all of the links on the page that are of length 2-3
// and put them on 

list_of_a = document.getElementsByTagName("a")

for (var i = 0; i < list_of_a.length; i++) { link = list_of_a[i]; contents = 
    link.text.split(' '); if (contents.length >= 2 && contents.length <= 3) 
    {console.log(link.text); }}




// the script below will present a box on the page to do a wikipedia search

javascript:function se(d) {return d.selection ? d.selection.createRange().text : 
    d.getSelection()} s = se(document); for (i=0; i<frames.length && !s; i++) 
    s = se(frames[i].document); if (!s || s=='') s = prompt
    ('Enter%20search%20terms%20for%20Wikipedia',''); open
    ('http://en.wikipedia.org' + (s ? '/w/index.php?title=Special:Search&search=' 
    + encodeURIComponent(s) : '')).focus();