/**
 * Created by admin on 9/18/14.
 */
    $(document).ready(function(){
        namespace='/test';
        var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
        socket.on('my response', function(msg){
            $('#content').empty()
            var arr=JSON.parse(msg.data);
            for(var i=0;i<msg.data.length;++i){
            //$.getJSON('msg.data')
            $('#content').append('<br>'+arr[i].user_name+': '+arr[i].msg);
            };
        });
        socket.on('room msg',function(msg){
            $('#content').append('<br>'+msg.user_name+': '+msg.data);
            });
        socket.on('update room list',function(msg){
            $('#room_list').empty()
            var arr=JSON.parse(msg.data)
            for(var i=0;i<msg.data.length;++i){
                var el=document.createElement("input");
                var del=document.createElement("input");
                el.type="submit";
                el.id=arr[i].chat_id;
                el.value=arr[i].name;
                $('#room_list').append(el);
                $(el).bind('click', function(){
                    var id = $(this).attr('id');
                    if (id>0){
                        socket.emit('my event',{data: id});
                        return false;}
                });
                del.type="submit";
                del.id=-arr[i].chat_id;
                del.value="del";
                $('#room_list').append(del);
                $(del).bind('click',function(){
                    var id=$(this).attr('id');
                    socket.emit('delete room',{data: -id});
                    return false;
                });
                $('#room_list').append('<br>');
            };

            });
        socket.on('find room result',function(msg){
            $('#result').empty()
            var arr=JSON.parse(msg.data)
            if(arr.length>0){
                $('#result').append('<h6>Click to join</h6>')
                for(var i=0;i<msg.data.length;++i){
                    var el=document.createElement("input");
                    el.type="submit";
                    el.id=arr[i].chat_id;
                    el.value=arr[i].name;
                    $('#result').append(el);
                    $(el).bind('click',function(){
                        var id=$(this).attr('id');
                        socket.emit('join room',{data: id});
                        $('#result').empty();
                        return false;
                    });
                };
            }else{
                $('#result').append('<h6>Rooms find: 0</h6>');
            ;}
        });

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
    });


