// Create a function that will receive data sent from the server

ajaxRequest.onreadystatechange = function(){
    if(ajaxRequest.readyState == 4){
        document.myForm.time.value = ajaxRequest.responseText;
    }
}