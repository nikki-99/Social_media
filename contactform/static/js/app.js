
function renderModal() {
  $(".ui.modal").modal("show");
}
var i = 0;
function buttonClick() {
    document.getElementById('inc').value = ++i;
}


function close_flash_message(){  
  document.all.altmsg.style.display='none';
  return false;  
}

