function confirmarEliminar(url){

    if (confirm("Está seguro?")){
        location.href = url;
    }    

}

function buscarAprendices(url){
    dato = $('#dato').val();
    resultado = $('#respuesta');
    token = $('input[name="csrfmiddlewaretoken"]').val();
    console.log("Token:" + token);
    $.ajax({
        url: url,
        type: 'post',
        data: { "dato": dato, "csrfmiddlewaretoken": token},
        //dataType: 'json',
        success: function(respuesta){
            resultado.html(respuesta);
        },
        error: function(error){
            console.log("Error" + error);
        }
    });
}

function buscarUsuarios(url){
    dato = $('#dato').val();
    resultado = $('#respuesta');
    token = $('input[name="csrfmiddlewaretoken"]').val();
    //console.log("Token:" + token);
    $.ajax({
        url: url,
        type: 'post',
        data: { "dato": dato, "csrfmiddlewaretoken": token},
        //dataType: 'json',
        success: function(respuesta){
            resultado.html(respuesta);
        },
        error: function(error){
            console.log("Error" + error);
        }
    });
}