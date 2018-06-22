function showToast() {
    // Get the snackbar DIV
    var x = document.getElementById("snackbar");

    // Add the "show" class to DIV
    x.innerHTML = "Paragraph changed!";
    x.className = "show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
}

function showToastTemp(message) {
    // Get the snackbar DIV

    var $div = $('<div />').appendTo('body');
	$div.attr('id', 'snackbar');

	$div.text(message)

	$div.addClass('show')
    
    // After 3 seconds, remove the show class from DIV
   setTimeout(function(){ $div.removeClass("show"); $div.remove()}, 2000);
}