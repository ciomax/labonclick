$(document).ready(function(){
    $('.accordion-button').on('show.bs.collapse', function (e) {
        $('.collapse').collapse("false")
    })
})