$(document).ready(function(){

	// Constructs the suggestion engine
	function customTokenizer(datum) {
	  var nameTokens = Bloodhound.tokenizers.whitespace(datum.name);
	  //var ownerTokens = Bloodhound.tokenizers.whitespace(datum.owner);
	  //var languageTokens = Bloodhound.tokenizers.whitespace(datum.language);

	  return nameTokens//.concat(ownerTokens).concat(languageTokens);
	}

	function typeaheadCallback(postResponse){
		if (postResponse.isLinked == true) {
			$('#extLinkName').val(postResponse.ext_link_string);
			$('#extLink').val(postResponse.ext_link)
		}
		else
		{
			console.log(false)
		}
	}


    var inputs = new Bloodhound({
    	//local: [{name: "James item", code:1},{name: "Claire item", code:2}],
    	//local: [{"code": "acdf091633109d3b6b7744a602720412", "name": "Input of Unlinked input"}, {"code": "bc1d1b9e06255d25691d4bc25cbed054", "name": "Input of Quartz - linked"}, {"code": "440891b98348acaa325bb80b1e0080fb", "name": "Input of Energy, electricity"}],
    	//identify: function(obj) { return obj.code; },
        datumTokenizer: customTokenizer,// Bloodhound.tokenizers.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        // The url points to a json file that contains an array of input names
        //prefetch: './inputs.json',
        prefetch: {
	        url: 'inputs.json',
	        transform: function(list) {
	            return $.map(list, function(item) {
	                return {
	                    name: item.name,
	                    code: item.code,
	                    //etc:item.etc
	                };
	                
	            });
	        },
	        cache:false,
	    },
        
        //local : ['Energy, electricity', 'Energy, heat', 'Potassium silicate', 'Sodium silicate']
        
    });
    console.log (inputs)

    function createNewTemplate(){
		current_input = $('#inputName').val()
		$create_new = $('<div class="tt-footer"><p>Create new input called <strong>'+current_input+'<strong></p></div>')
		$create_new.click(function(){
			console.log('create_new')
			$('.typeahead').typeahead('close');
		})
		return $create_new
    }

    // Initializing the typeahead with remote dataset
    $('.typeahead').typeahead({
			minLength: 1,
		 	highlight: true
    	},
    	{
	        name: 'inputs',
	        display:'name',
	        source: inputs,
	        templates:{
	        	header: '<div class="tt-header"><p>Reuse existing input...</p></div>',
	        	footer: createNewTemplate,
	        	notFound: createNewTemplate,
			},
    	}
    );

    function eventHandler(obj, suggestion){
    	console.log(suggestion)
    	var postData ={
    		'action': 'inputLookup',
    		'code': suggestion.code,
    	}
    	$.post('/process_post',
    	 	postData, 
    	 	function(data, status, xhr){
	          if(status == 'success'){
	            typeaheadCallback(data)
	          }
	        }, 
	        "json");
    }
    
	$('#inputName').bind('typeahead:selected', function(obj, suggestion) {  
			console.log('selected');
			eventHandler(obj, suggestion);
	});
	$('#inputName').bind('typeahead:autocomplete', function(obj, suggestion) {  
			console.log('autocomplete');
			eventHandler(obj, suggestion);
			$('.tt-footer').addClass('hide')
	});

	$('#inputName').keypress(function(e){
		if(e.keyCode==13){
			console.log('enter')
		}
	});

    $('#inputName').keydown(function(e){
    	if(e.keyCode==8 || e.keyCode==46){
    		console.log('delete/backspace')
    		$('#extLinkName').val('');
			$('#extLink').val('')
    	}
    });

});