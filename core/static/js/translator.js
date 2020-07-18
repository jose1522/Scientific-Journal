function getTranslation(language, text){
    var api_url = window.location.origin+"/api/translate"
    var body = {
          "sourceText": "Hello world",
          "targetLanguage": "de"
        }

    $.ajax({
        url: api_url,
        contentType: "application/json",
        dataType: 'json',
        data: body,
        success: function(result){
            console.log(result);
        }
    })
}

function getInnerHTML(){

}

function setInnerHTML(){

}

$( document ).ready(function() {getTranslation('a','b')});