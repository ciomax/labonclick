$(document).ready(function (){
  $('#sidebarCollapse').on('click', function() {
    $('#sidebar').toggleClass('active');
  });
});


$(".nav-link").hover(
    function() {
      $( this ).addClass( "active" );
    }, function() {
      $( this ).removeClass( "active" );
    }
  );

$('.equipment-btn').click(function(){
  $('.collapse').toggleClass("show");
  // console.log('clicked');
});

// sample
// $(document).ready(function(){
//     $(".btn").on('click', function(){
//         $("#myCollapsible").toggleClass('show');
//     });
// });




$(document).ready(function(){
  $('.accordion-list > li > .answer').hide();

  $('.accordion-list > li').click(function() {
    if ($(this).hasClass("active")) {
      $(this).removeClass("active").find(".answer").slideUp();
    } else {
      $(".accordion-list > li.active .answer").slideUp();
      // $(".accordion-list > li.active").removeClass("active");
      $(this).addClass("active").find(".answer").slideDown();
    }
    return false;
  });

});


$(document).ready(function(){
  $('.accordion-button').on('click', function() {
    if ($(this).hasClass("collapsed")) {
      $(this).removeClass("collapsed").find(".accordion-collapse").toggleClass('show');
      $(this).attr('aria-expanded', 'true');
      $(this).parent().next().addClass('show');
    } else {
      $(this).addClass("collapsed");
      $(this).attr('aria-expanded', 'false');
      $(this).parent().next().removeClass('show');
    }
    return false;
  });

});


// Setup details. tabs
$(document).ready(function() {
  $('.setuptab').on('click', function() {
    var t = $(this).attr('id');
    console.log('clicked')
    $('#myTab li a').attr('aria-selected', 'false');
    $(this).attr('aria-selected', 'true');
    $('.tab-pane').removeClass('active show')
    $('#'+ t + 'C').addClass('active show')
  });
});
