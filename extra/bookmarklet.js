function load_jquery(next_function) {
  if (typeof jQuery != "undefined") {
    return next_function();
  }
  function getScript(){
    var script=document.createElement('script');
    script.src="http://code.jquery.com/jquery-latest.min.js";
    var head=document.getElementsByTagName('head')[0],
    done=false;

    script.onload=script.onreadystatechange = function(){
      if ( !done && (!this.readyState
       || this.readyState == 'loaded'
       || this.readyState == 'complete') ) {
        done=true;
        next_function();
        script.onload = script.onreadystatechange = null;
        head.removeChild(script);
      }
    };

    head.appendChild(script);
  };
  getScript();
};

function scan_for_names() {
  var links = document.getElementsByTagName("a");
  var clean_links = [];
  var names = [];
  for (var i = 0; i < links.length; i++) {
    link = links[i];
    var text = $.trim(link.innerText);
    var pattern = /back to top/;

    var num_words = text.split(" ").length;

    if (num_words < 2 || num_words > 4) {
      continue;
    }
    
    if (/back to top/.test(text)) {
      continue;
    }

    if (/See Full List/.test(text)) {
      continue;
    }
    if (/Sign In/.test(text)) {
      continue;
    }

    clean_links.push(link);
    names.push(text);
  }
  return names;
};
/* whatever is a list of names that is scanned form the a-tags in the */
function send_names(whatever) { 
  $.post( "http://localhost:5000/receive_names/1", 
    {"names": whatever}, 
    function(connections){
      if ($.isEmptyObject(connections))  {
        alert("You have no connections on this page");
      }
      else
      {
        alert(JSON.stringify(connections));             
      }
      return false; 
    });
}

function scan_and_send() {
  var names = scan_for_names();
  send_names(names);
};

load_jquery(scan_and_send);