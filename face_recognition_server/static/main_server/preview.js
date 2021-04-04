const value = JSON.parse(document.getElementById('preview_script_data').textContent);
let time_data = value['time_data'];
let keys = Object.keys(time_data);

let test_el = document.querySelector("#test");
let cur_canvas = document.getElementById('screen_preview');

let cur_ind = 0

// Object.keys(value).forEach(function(key) {
//     let val = value[key];
// });

// AJAX for posting
function create_post() {
    console.log("create post is working!") // sanity check
    $.ajax({
        url : "create_post/", // the endpoint
        type : "POST", // http method
        data : { the_post : $('#post-text').val() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $('#post-text').val(''); // remove the value from the input
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

document.getElementById('btn_prev').addEventListener('click', function() {
    cur_ind -= 1
    set_canvas_frame_by_ind(cur_canvas, keys[cur_ind])
});

document.getElementById('btn_next').addEventListener('click', function() {
    cur_ind += 1
    set_canvas_frame_by_ind(cur_canvas, keys[cur_ind])
});

function set_canvas_frame_by_ind(canvas, ind){
    $.ajax({
        type:'POST',
        url:'',
        data:{
            ind: ind
        },
        success:function(json){
            bitmap = json['frame']
            set_data_on_canvas(bitmap, canvas)
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
    // xhr.send(JSON.stringify(send_data));
};


function set_data_on_canvas(dataset, canvas){
    
    canvas.style.width = dataset[0].length + 'px';
    canvas.style.height = dataset.length + 'px';
    canvas.setAttribute('width', dataset[0].length + 'px');
    canvas.setAttribute('height', dataset.length + 'px');

    var canvasWidth  = canvas.width;
    var canvasHeight = canvas.height;
    var ctx = canvas.getContext('2d');
    var imageData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);

    var buf = new ArrayBuffer(imageData.data.length);
    var buf8 = new Uint8ClampedArray(buf);
    var data = new Uint32Array(buf);

    for (var y = 0; y < canvasHeight; ++y) {
        for (var x = 0; x < canvasWidth; ++x) {
            var value = dataset[y][x];
            data[y * canvasWidth + x] =
                (255      << 24) |    // alpha
                (value[2] << 16) |    // blue
                (value[1] <<  8) |    // green
                 value[0];            // red
        }
    }

    imageData.data.set(buf8);

    ctx.putImageData(imageData, 0, 0);
}

set_canvas_frame_by_ind(cur_canvas, keys[cur_ind]);