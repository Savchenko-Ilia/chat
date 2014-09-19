/**
 * Created by admin on 8/31/14.
 */
$('input[type=submit]').bind('click', function(){
            var id = $(this).attr('id');
            if (id>0){
                socket.emit('my event',{data: id});
                return false;}
            else if(id==0){
                socket.emit('my room event', {data: $('#room_data').val()});
                return false;
                }
            else if(id=='id_add_room'){
                socket.emit('add room', {data: $('#add_room').val()});
                $('#add_room').val('');
                return false;
                }
            else if(id<0){
                socket.emit('delete room', {data: -id});
                return false;
                }
            else if(id=='id_join_room'){
                socket.emit('join room', {data: $('#join_room').val(),id: $(this).find("h5").data("value") });
                return false;
                }
            else if(id=='id_find_room'){
                socket.emit('find room', {data: $('#find_room').val()});
                 $('#find_room').val('');
                return false;
                }
            else{
                $('#room_list').append('<br>'+'Id click:'+id);
                return false;
                }
        });