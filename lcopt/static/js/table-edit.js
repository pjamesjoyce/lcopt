$(document).ready(function(){


	var $TABLE = $('#table');
	var $BTN = $('#export-btn');
	var $EXPORT = $('#export');

	// A few jQuery helpers for exporting only
	jQuery.fn.pop = [].pop;
	jQuery.fn.shift = [].shift;

	// Post to the provided URL with the specified parameters.
	function post(path, parameters) {
	    var form = $('<form></form>');

	    form.attr("method", "post");
	    form.attr("action", path);

	    $.each(parameters, function(key, value) {
	        var field = $('<input></input>');

	        field.attr("type", "hidden");
	        field.attr("name", key);
	        field.attr("value", value);

	        form.append(field);
	    });

	    // The form needs to be a part of the document in
	    // order for us to be able to submit it.
	    $(document.body).append(form);
	    form.submit();
	}

	$BTN.click(function () {
	  var $rows = $TABLE.find('tr:not(:hidden)');
	  var headers = [];
	  var data = [];
	  
	  // Get the headers (add special header logic here)
	  $($rows.shift()).find('th:not(:empty)').each(function () {
	    headers.push($(this).text());
	  });
	  
	  // Turn all existing rows into a loopable array
	  $rows.each(function () {
	    var $td = $(this).find('td');
	    var h = {};
	    
	    // Use the headers from earlier to name our hash keys
	    headers.forEach(function (header, i) {
	      h[header] = $td.eq(i).text();   
	    });
	    
	    data.push(h);
	  });
	  
	  // Output the result
	  //$EXPORT.text(JSON.stringify(data));
	  //$.post("/",
	  //     JSON.stringify(data),
	  //      function(data,status){
	  //          alert("Data: " + data + "\nStatus: " + status);
	  //      });
	//	});
	var url = "/parse_parameters"
	/*$.ajax(url, {
	    data : JSON.stringify(data),
	    contentType : 'application/json',
	    type : 'POST',
	    success: function(data) { alert('data: ' + data); }
		});*/

	postData ={
		'action':'parse_parameters',
		'data' : JSON.stringify(data)
	}
   	
   	$.post('/process_post', postData);

   	window.location.replace("/");

	});

	


	var myTable = $('#myTable'),
    iter = 0;

	$('#btnAddCol').click(function () {
	     myTable.find('tr').each(function(){
	         var trow = $(this);
	         if(trow.index() === 0){
	         	count = trow.find('.ps_name').length
	             trow.append('<th class="ps_name">ParameterSet_'+(count+1)+'</th>');
	         }else{
	         	last_item = trow.find('td:last')
	         	
	            trow.append('<td contenteditable="true" class="new_item">'+ last_item.text() +'</td>');
	         }
	     });
	     iter += 1;
	});

})//end of document.ready