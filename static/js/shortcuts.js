$(document).ready(function() {
    ctrl = false;
    alt = false;
});

$(document).keydown(function(event) {
    // Update state keys
    if (event.which == "17")
        ctrl = true;
    else if (event.which == "18")
        alt = true;

    // CTRL+K will focus on the search bar
    else if (ctrl && event.which == "75") {
        event.stopPropagation();
        event.preventDefault();
        $("#search-term")[0].focus();
    }

    // CTRL+L will trigger the login/logout
    else if (ctrl && event.which == "76") {
        event.stopPropagation();
        event.preventDefault();
        window.location.href = $("#toggle_login")[0].href;
    }
});

$(document).keyup(function(event) {
    // Update state keys
    if (event.which == "17")
        ctrl = false;
    else if (event.which == "18")
        alt = false;
});
