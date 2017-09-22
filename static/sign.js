var reload_interval = 60000;
var hash_url = '/sign/hash/';
var i = 0;
var l = 0;
var branch;
var page_hash;
var infos;
var slides;
var n;

window.onload = function(e) {
    branch = document.getElementById('main').getAttribute('data-branch');
    page_hash = document.getElementById('main').getAttribute('data-hash');
    infos = document.getElementsByClassName('info');
    slides = document.getElementsByClassName('slide');
    n = infos.length;
    window.setInterval(checkReload, reload_interval);
    nextSlide();
};

function nextSlide() {
    var x = i%n;
    var d = infos[x].getAttribute('data-duration');
    infos[l].classList.remove('selected');
    slides[l].classList.remove('selected');
    infos[x].classList.add('selected');
    slides[x].classList.add('selected');
    l = x;
    i++;
    setTimeout(nextSlide, d * 1000);
}

function checkReload() {
    fetch(hash_url + branch).then(function(response) {
        return response.json();
    }).then(function(j) {
        if (j.value != page_hash) {
            page_hash = j.value;
            window.location.reload(true);
        }
    });
}
