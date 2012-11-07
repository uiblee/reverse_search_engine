/* Reverse search engine for connections
  
I. User creates a profile for the ChromeApp-Extension
    A. The profile would be an entry in the database of the program
    B. This is the information for each user:
        1. Username/Email
        2. User Password
        3. LinkedIn account 
            a. password
        4. Facebook account 
            a. password
        5. Google contacts/email account 
            a. password
        6. CRM account 
            a. password
        7. Twitter account 
            a. password
        8. Keywords chosen by the User to also be regularly searching for    

II. As a ChromeApp-Extension, pull list of terms (People, Organizations, Places??) from 
    website using javascript
    A. need to figure out how to get text that's not a link...but still important
        basically how to pull pronouns
        1. pulling anything with capital letter??
            a. pulling anything with University in it
            b. company names that might be in real world dictionary
            c. Names followed by acronyms 
        2. refining how to get names...typical structure of name e.g. Marc A. Hunter
    B. need to weed out words that are in the dictionary and shouldn't be looked up
        1. if all parts of link are in the dictionary, throw out

III. Send the list to Python / Flask
    A. Use Ajax request to send list fo keyphrases to server where Python code is located
    A. Have all of the keyphrases printed to a text file (website_text.txt)
    B. Use python functions to take keyphrases from website_text.txt and run through functions
        to check if in LinkedIn, Facebook, google contacts, CRM, user's keywords, twitter accounts
    C. If the keyphrase is in one of the User accounts, flag the keyphrase as "connected" and make
        a dictionary entry with the value as another dictionary listing each "connector" social site 
        as a key and a short fill-in sentence as the value
        1. example: "Lindsey is a friend on facebook,"

IV. Send the dictionary of "connected" keyphrases back to javascript/link/ChromeApp-Extension
    A. display phrases on webpage as being highlighted with an ability to mouse-over to display
        values of dictionary
    B. Have an optional print out to excel or pdf...would need to format to read easily

V. Each search would be saved by the program (or at least how each website gets parsed...the 
    website_text.txt file would get saved as associated to the web address)

VI. The User would be able to log-in and log-out by clicking on the ChromeApp-Extension
    They could also manage options for the search or the output

 

  pg_ctl start -D /Users/student/Fall2012/reverse_search/reverse_search_engine/ratings/postgres/data -l /Users/student/Fall2012/reverse_search/reverse_search_engine/ratings/postgres/logfile


  */




/* the script below will pull all of the links, splits them by their spaces,
 then prints the links that are 2-3 parts in length */

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

//what goes in Chrome ()
javascript:list_of_a = document.getElementsByTagName("a")for (var i = 0; i < list_of_a.length; i++) { link = list_of_a[i]; contents = link.text.split(' '); if (contents.length >= 2 && contents.length <= 3) {console.log(link.text); }}