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
            lang = document.cookie.split('=')[1]
            getTranslation(this, 'a', lang)
        })
    })
}

async function translateDoc(){
    let arrayofPromises = [
        getInnerHTML('a'),
        getInnerHTML('p'),
        getInnerHTML('h1'),
        getInnerHTML('label'),
        getInnerHTML('th'),
        getInnerHTML('#card-header')
    ]
    await process(arrayofPromises);
    //quitar animación de loading
}

async function process(arrayofPromises) {
    let responses = await Promise.all(arrayofPromises);
}

function deleteAllCookies() {
    var cookies = document.cookie.replace(" ","").split(";");
    console.log(cookies)
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        console.log(name)
        document.cookie = name + "= ;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
}

function setLanguageCookie(language){
    deleteAllCookies()
    setTimeout(function(){
        document.cookie = "lang="+language+";path=/admin"
        location.reload()
    }, 1);

}

$(document).ready(async function() {
    // cargar animación de loading
    console.log(document.cookie)
    if ( !['lang=en',null,NaN,""].includes(document.cookie)) {
        translateDoc();
    }
});
