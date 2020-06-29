//Modules
const unfluff = require('unfluff');
const cheerio = require('cheerio');
const request = require('request');
//Variables and Consts
const url = 'https://www.nbcnews.com/news/us-news/everybody-loved-george-familiar-refrain-about-man-who-showed-everybody-n1227371'

//Main

request(url, (error, response, html) => {
    if (!error && response.statusCode == 200){
        console.log(html);
        data = unfluff(html);
        console.log(data.text);
        console.log(data.author)
        author = data.author
        console.log(occurrences(data.text, " he ", false))
    }

})

function occurrences(string, subString, allowOverlapping) {

    string += "";
    subString += "";
    if (subString.length <= 0) return (string.length + 1);

    var n = 0,
        pos = 0,
        step = allowOverlapping ? 1 : subString.length;

    while (true) {
        pos = string.indexOf(subString, pos);
        if (pos >= 0) {
            ++n;
            pos += step;
        } else break;
    }
    return n;
}




