$(document).ready(function(){
  $('.click-row').click(function(){
    window.location = $(this).data('href');
    return false;
  });
});

