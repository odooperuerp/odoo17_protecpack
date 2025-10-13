$(function(){
    function buscar_documento() {
        var data = {
            // @ts-ignore
                "serie": $("#serie").val(),
                "correlativo": $("#correlativo").val(),
                "invoice_date":$("#invoice_date").val(),
                "vat":$("#vat").val(),
                "total":$("#total").val()

        }
        $.post("/consulta_cpe", data).done(function(response) {
            $("#documento").html(response)
        })
    }

    $('form[name="form_buscar_documento"]').submit(function(event){
        event.preventDefault()
        buscar_documento()
  })
});