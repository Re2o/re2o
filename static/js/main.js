function adjustHeader(){
    /* This function is here to adjust the header if the header navbar
    goes into two lines. This can't happen if the width is sm or less,
    and we shouldn't adjust in this case. */
    if ($(window).width() >= 768) {
        $('body').css('padding-top', $("#navbar-header").height());
        $('.sidenav-left').css('top', $("#navbar-header").height());
    } else {
        $('body').css('padding-top', '');
        $('.sidenav-left').css('top', '');
    }
}

function listenSubmenu() {
    /* Add listeners on sm screen or less for submenus. */
    if ($(window).width() < 767) {
        $('.dropdown-menu a').click(function (e) {
            if ($(this).next('.submenu').length) {
                e.preventDefault();
                $(this).next('.submenu').toggle();
            }
            $('.dropdown').on('hide.bs.dropdown', function () {
                $(this).find('.submenu').hide();
            })
        });
    }
}

/* We need to apply those functions at init and when the screen is resized. */

$(window).resize(function () {
   adjustHeader();
   listenSubmenu();
});

adjustHeader();
listenSubmenu();


$(document).on('click', '.dropdown-menu', function (e) {
    e.stopPropagation();
});