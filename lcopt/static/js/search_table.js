var UNIT_CHOICES = {
    'Mass': [
        ['kg',  'kilogram'],
        ['g',  'gram'],
    ]
    ,
    'Energy': [
        ['kWh',  'kilowatt hour'],
        ['Wh',  'watt hour'],
        ['GJ',  'gigajoule'],
        ['kJ',  'kilojoule'],
        ['MJ',  'megajoule'],
    ]
    ,
    'Volume': [
        ['l',  'litre'],
        ['m3',  'cubic meter'],
    ]
    ,
    'Radioactivity': [
        ['Bq',  'Becquerel'],
        ['kBq',  'kilo Becquerel'],
    ]
    ,
    'Time': [
        ['a',  'year'],
        ['h',  'hour'],
    ]
    ,
    'Amount': [
        ['p',  'unit'],
    ]
    ,
    'Area':[
        ['ha',  'hectare'],
        ['m2',  'square meter'],
    ],
    'Transport':[
        ['kgkm',  'kilogram kilometer'],
        ['tkm',  'ton kilometer'],
        ['personkm',  'person kilometer'],
        ['vkm',  'vehicle kilometer'],
    ],
    'Distance':[
        ['km',  'kilometer'],
        ['m',  'meter'],
    ],
    'Other':[
        ['lu',  'livestock unit'],
        ['m*year',  'meter-year'],
        ['m2*year',  'square meter-year'],
        ['m3*year',  'cubic meter-year'],
        ['kg sw',  'kilogram separative work unit'],
        ['km*year',  'kilometer-year'],
        ['EUR2003', 'EUR2003']
    ]
} 



var render_results_as_table = function(results, format){

  console.log(results);
  unit_check_map = {};
  unit_keys = [];

  for(i in UNIT_CHOICES){
    
    for(j in UNIT_CHOICES[i]){
      unit_check_map[UNIT_CHOICES[i][j][0]] = [UNIT_CHOICES[i][j][1]];
      unit_keys.push(UNIT_CHOICES[i][j][0])
    };
  };

  console.log(unit_check_map);
  console.log(unit_keys)

  $table = $('<table class="table table-fixed container" id="search_result_table"></table>')

  html="";
  result_count = 0;

  for(var key in results){
    if (results.hasOwnProperty(key)) {
      var item = results[key];

      if($.inArray(item['unit'], unit_keys) != -1){
        display_unit = unit_check_map[item['unit']];
      }else{
        display_unit = item['unit'];
      }

      if (item.hasOwnProperty('database')) {database_name = item['database'];} else {database_name = '<b>This model</b>';}

      if (format == 'ecoinvent'){
        html += `<tr id="`+ key +`" class="col-xs-12 clickable-row">
          <td class="col-xs-5 name_field">`+item['name']+`</td> 
          <td class="col-xs-2 location_field">` + item['location'] + `</td> 
          <td class="col-xs-2 unit_field">` + display_unit +`</td> 
          <td class="col-xs-3">`+ database_name +`</td>
          </tr>`;

        $table.html(`<thead><tr class="col-xs-12">
          <th class="col-xs-5">Name</th>
          <th class="col-xs-2">Location</th>
          <th class="col-xs-2">Unit</th>
          <th class="col-xs-3">Database</th>
          </tr></thead><tbody>` + html + "</tbody>");
      }
      else if (format == 'biosphere'){

        if(item['type'] == 'emission'){
          html += `<tr id="`+ key +`" class="col-xs-12 clickable-row">
          <td class="col-xs-4 name_field">`+item['name']+`</td> 
          <td class="col-xs-4 location_field">Emission to ` + item['categories'] + `</td> 
          <td class="col-xs-2 unit_field">` + item['unit'] +`</td> 
          <td class="col-xs-2">`+ item['database'] +`</td>
          </tr>`;

        }else{
          html += `<tr id="`+ key +`" class="col-xs-12 clickable-row">
          <td class="col-xs-4 name_field">`+item['name']+`</td> 
          <td class="col-xs-4 location_field">` + item['categories'] + `</td> 
          <td class="col-xs-2 unit_field">` + item['unit'] +`</td> 
          <td class="col-xs-2">`+ item['database'] +`</td>
          </tr>`;
        
        }

        $table.html(`<thead><tr class="col-xs-12">
          <th class="col-xs-4">Name</th>
          <th class="col-xs-4">Category</th>
          <th class="col-xs-2">Unit</th>
          <th class="col-xs-2">Database</th>
          </tr></thead><tbody>` + html + "</tbody>");

      }

      result_count++;
  }
  }
  

  $table.on('click', '.clickable-row', function(event) {
    $(this).addClass('active').siblings().removeClass('active');
  });

  return $table;

}

