var approx_maps = [
	[],
	[[0, 0]],
	[[0, 0], [0, 1], [1, 0], [1, 1]],
	[[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]],
	[[0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [1, 3], [2, 0], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2]],
	[[0, 1], [0, 2], [0, 3], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]]]


var anim_length = 200;
var ws;

var caster_controller;



var joined_crid;
var objects = {};
var creatures;
var zero_pad = "0000";

var	map = {};
var object_map = {};
var coords = [];

function pad_with_zeroes(coord){
	return (zero_pad+coord).slice(-zero_pad.length)
}

function make_str_coord(coord){
	return pad_with_zeroes(coord[0])+":"+pad_with_zeroes(coord[1])
}

var populate = function(crtr){
     tabBody=document.getElementById("creatures");
     row=document.createElement("TR");
     cell_id = document.createElement("TD");
     cell_cls = document.createElement("TD");
     cell_name = document.createElement("TD");
     cell_use = document.createElement("BUTTON");
     cell_use.innerText = "JOIN";
     cell_use.onclick = function(){
     	ws.send(JSON.stringify(
     		{"what":"join",
     		 "crid":crtr.id
     		}
     ));
     }
     textnode_id=document.createTextNode(crtr.id);
     textnode_cls=document.createTextNode(crtr.cls);
     textnode_name=document.createTextNode(crtr.name);
     cell_id.appendChild(textnode_id);
     cell_cls.appendChild(textnode_cls);
     cell_name.appendChild(textnode_name);
     row.appendChild(cell_id);
     row.appendChild(cell_cls);
     row.appendChild(cell_name);
     row.appendChild(cell_use);
     tabBody.appendChild(row);
}

function add_object_to_map(o){
	//TODO: move somewhere more appropriate
	if (o.id == joined_crid){
		$('#cr_status').html(o.coords.join(', '))
	}
	approx_maps[o.size].map(
		function(c){
			object_map[make_str_coord([c[0]+o.coords[0], c[1]+o.coords[1]])] = o;
		}
	);
	objects[o.id] = o;
}

function draw_field(){
	coords.sort();
	mincoord = coords[0].split(':');
	map.xmin = parseInt(mincoord[0]);
	map.ymin = parseInt(mincoord[1]);
	
	maxcoord = coords[coords.length-1].split(':');
	map.xmax = parseInt(maxcoord[0]);
	map.ymax = parseInt(maxcoord[1]);
	str = "";
	models = {"kob1":"@",
	          "drak1":"&",
	          "sword":")",
	          "wall":"#",
	          "floor":"." };
	for(var y = map.ymin; y<=map.ymax; y++){
		str += "<tr>";
		for(var x = map.xmin; x<=map.xmax; x++){
			str_coord = make_str_coord([x,y])
			if(str_coord in object_map){
				o = object_map[str_coord];
				ch = models[o.model];
				cls = "object";
				if (o.id == joined_crid){
					cls += " my_cr";
				}
				str += '<td class="'+cls+'", oid='+o.id+' >'+ch +'</td>';
			} else if(str_coord in map){
				t = map[str_coord];
				ch = models[t.type];
				str += '<td xpos="'+x+'" ypos="'+y+'" t_type="'+t.type+'" >'+ch+'</td>';
			} else {
				str += '<td class="t_undef"> </td>';
			}
		}
		str += '</tr>';
	}
	
	$("#field").html(str);

}
function connect(){
	ws = new WebSocket('ws://'+document.location.host);

	ws.onmessage = function(message) {
		document.getElementsByName('output')[0].value += message.data+'\n';
		var obj = JSON.parse(message.data)
		switch(obj.what){
		
		case "login":
			$('#login_form').hide(anim_length);
			creatures = Array();
			obj.creatures.map(function(crtr){
				creatures[crtr.id] = crtr;
				populate(crtr)});
				
			$('#creatures').show(anim_length);
			break;
			
		case "joined":
			$('#creatures').hide(anim_length);
			$('#cr_info').show(anim_length);
			$('#cr_name').html(creatures[obj.crid].name);
			joined_crid = obj.crid;
			break;
		/*
		case "environment":
			obj.cells.map(function(cell){
				
				text_coords = make_str_coord(cell.coords);
				coords.push(text_coords)
				map[text_coords] = cell;
			});
			obj.objects.map(add_object_to_map);
			draw_field();
			$("#game_turn").html(obj.turn);
			break;
			
		case "responses":
			//TODO: register enter/exit
			obj.new_objects.map(add_object_to_map)
			draw_field();
			$("#game_turn").html(obj.turn+1);
			break;
		*/
		}
	};
	
	ws.onclose = function(){
		document.getElementsByName('output')[0].value += "DISCONNECTED\n";
	}
}
function do_login(form)
{
	f = document.getElementById('login_form')
	ws.send(JSON.stringify({what:"login", 
	                        login:f.login.value,
	                        passw:f.passw.value}))
	return false;
}

$(function(){
	$('body').on('click','#field td', function(e){
		xpos = e.toElement.getAttribute('xpos')
		ypos = e.toElement.getAttribute('ypos')
		//alert(xpos+", "+ypos);
	});
	
	function update_info(){
		var hoof = $('.object_hovered');
		var sel = $('.object_selected');
		obj = false;
		if (hoof.length != 0){
			obj = objects[hoof.attr('oid')]
		} else if (sel.length != 0) {
			obj = objects[sel.attr('oid')]
		}
		if (obj == false){
			str = 'Nothing selected';
		} else {
			str = "<ul>";
			for (var p in obj){
				str += '<li>'+p+' — '+obj[p]+'</li>';
			}
		}
		$('#target_description').html(str);
	}
	
	function get_td_by_object(o){
		return $('td[oid="'+$(o).attr('oid')+'"]');
	}
	
	$('#field').on('mouseenter mouseleave','td.object', function(){
		get_td_by_object(this).toggleClass('object_hovered');
		update_info();
	});
	
	$('#field').on('click','td.object', function(){
		if ($(this).attr('oid') == joined_crid){
			return false;
		}
		get_td_by_object(this).toggleClass('object_selected');
		$('.object_selected').not('[oid='+$(this).attr('oid')+']').removeClass('object_selected');
		update_info();
		
	});
	
	
});

atom.declare( 'Caster.Controller', {
    initialize: function () {
    	this.engine = new TileEngine({
    		size: new Size(5,5),
    		cellSize: new Size(25,25),
    		cellMargin: new Size(1,1),
    		defaultValue: 'closed'
    	}).setMethod({'#':this.draw.bind(this),
    	              '.':this.draw.bind(this)}
    	              );
    	
    	this.app = new App({
			size  : new Size(640,480),
			appendTo: '#field',
			simple: true
		});
	
		
		this.element = TileEngine.Element.app( this.app, this.engine );
		for (var i=0; i<5; i++){
			for (var j=0; j<5; j++){
				this.engine.getCellByIndex(new Point(i,j)).value = Math.random()>0.5?'#':'.';
			}
		}
    },
    draw: function (ctx, cell) {
    	//ctx.font = "23pt monospace";
    	ctx.fill(cell.rectangle, '#444');
    	for (var m = 0; m<2; m++){
    		    coord_diff = [[-1,0],[0,-1]][m];
    		    neigh_coord = cell.point.clone().move(coord_diff);
    			neigh_cell = cell.engine.getCellByIndex(neigh_coord);
    			if ((neigh_cell != null) && (neigh_cell.value != cell.value)){
    				from = cell.rectangle.from;
    				to = coord_diff[1]?cell.rectangle.topRight:cell.rectangle.bottomLeft;
    				//ctx.stroke(Rectangle({center:from, size:[3,3]}),'white')
    				//ctx.stroke(Rectangle({center:to, size:[3,3]}),'white')
    				ctx.save()
    				//.clip(cell.rectangle)
    				.set({ lineWidth: 2 })
    				.stroke(new Line(from, to),'#999')
    				.restore();
    			}
    	}
    	//ctx.fillText("#", cell.rectangle.bottomLeft.x, cell.rectangle.bottomLeft.y);
    	//console.log(cell);
    	//console.log(ctx);
    	ctx.text({
    	text:cell.value,
    	to: cell.rectangle,
    	align:'center',
    	size:18,
    	family:'monospace'
    	})
    }

});


LibCanvas.extract();

atom.dom(function () {
    caster_controller = new Caster.Controller();
});
