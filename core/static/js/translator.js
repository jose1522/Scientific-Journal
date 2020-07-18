function getTranslation(element, sourceText, targetLanguage) {
    return new Promise( (resolve) => {
        let api_url = window.location.origin+"/api/translate"
        let body = {
              "sourceText": element.innerHTML,
              "targetLanguage": targetLanguage
            }
    
        $.ajax({
            url: api_url,
            contentType: "application/json",
            dataType: 'json',
            data: body,
            success: function(result){
                // console.log(result['text'])
                // console.log(element)
                element.innerHTML = result['text']
            }
        })

    })

}

function getInnerHTML(tagName){
    return new Promise( (resolve) => {
        $(tagName).each( function(index){
            getTranslation(this, 'a', 'de')
        })
    })
}

async function process(arrayOfPromises) {
    let responses = await Promise.all(arrayOfPromises);
}

$( document ).ready(async function() {
    // cargar animación de loading
    let arrayofPromises = [
        getInnerHTML('a'),
        getInnerHTML('p'),
        getInnerHTML('h1'),
        getInnerHTML('label'),
        getInnerHTML('th'),
        getInnerHTML('#card-header')
    ]
    await process(arrayOfPromises);
    //quitar animación de loading
});
