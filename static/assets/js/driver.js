
console.log("OK");

$.getJSON('/data/all.json', function(data) {
    var template = $("#book_template").html();
    var html = Mustache.render(template, data);
    $('#target').html(html);
});
