jsPlumb.ready(function(){

  $('.pull-down').each(function() {
    $(this).css('margin-top', $(this).parent().height()-$(this).height())
  }); 
  //jsPlumb.setContainer($('#sandbox_container'));

   var i = 0;

   $('#sandbox_container').dblclick(function(e){
     var newItem = $('<div>').attr('id', 'item_' + i).addClass('item');

     var title =  $('<div>').addClass('title').text('Item ' + i);

     var connect =  $('<div>').addClass('connect');

     offset = $('#sandbox_container').offset();

     newItem.css({
       'top': e.pageY - offset.top,
       'left': e.pageX - offset.left
     });

     newItem.append(title);
     newItem.append(connect);

     $('#sandbox_container').append(newItem);

     jsPlumb.makeTarget(newItem,{
       anchors: ['Left','Right', 'Bottom']
     });

     jsPlumb.makeSource(connect,{
       parent: newItem,
       anchors: ['Left','Right', 'Bottom'],
       connector: ['Flowchart']
     });

     jsPlumb.draggable(newItem,{
       containment: 'parent'
     });

     newItem.dblclick(function(e){
       jsPlumb.detachAllConnections($(this));
       $(this).remove();
       e.stopPropagation();
     });

     i++;

   });

});
