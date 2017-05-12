$(document).ready(function() {

console.log ('hello from dynamic table')

    function poll() {
        console.log('polling now')
        $.ajax({
            url: dt_targetPage,
            type: "post",
            dataType: "json",
            success: function(response) {
                console.log('success')
                data = JSON.parse(response)
                console.log(data)
            }
        });
    }

/*setInterval(function(){
    console.log('polling for live_data.json')
    console.log("here's the response...")
    poll()
    }
    , 3000);
*/
poll()
})