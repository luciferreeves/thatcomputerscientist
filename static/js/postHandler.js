function editComment(id) {
    document.getElementById('comment-body-' + id).style.display = 'none';
    document.getElementById('edit-form-' + id).style.display = 'block';
}

function cancelEdit(id) {
    document.getElementById('comment-body-' + id).style.display = 'block';
    document.getElementById('edit-form-' + id).style.display = 'none';
}

function cd() {
    // we will clear the user cookies
    document.cookie = 'anonymous_name=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'anonymous_email=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'anonymous_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.reload();
}

function toggleTips() {
    var tips = document.getElementById('tips');
    $('#tips').slideToggle('fast');
}

function toggleGotchas() {
    var gotchas = document.getElementById('gotchas');
    $('#gotchas').slideToggle('fast');
}

function toggleAnon() {
    $('#ancmClick').toggle();
    $('#anonymous-comment-form').slideToggle('fast');
};

function toggleCreds() {
    $('#creds').slideToggle('fast');
};

function lightsOff() {
    // #overlay. Go from 0.8 -> 0.9 opacity
    var currentStatus = $('#lightsStatus').attr('data-status');
    var windowWidth = document.documentElement.clientWidth;
    if (currentStatus == 'on') {
        $('#overlay').fadeTo('fast', 0.8);
        if (windowWidth > 480) {
            $('#sidebar').children().fadeTo('fast', 1);
            $('#header').fadeTo('fast', 1);
            $('#footer').fadeTo('fast', 1);
        }
        $('#lightsStatus').attr('data-status', 'off');
        $('#lightsStatus').attr('src', offImage);
    } else {
        $('#overlay').fadeTo('fast', 0.9);
        if (windowWidth > 480) {
            $('#sidebar').children().fadeTo('fast', 0.2);
            $('#header').fadeTo('fast', 0.2);
            $('#footer').fadeTo('fast', 0.2);
        }
        $('#lightsStatus').attr('data-status', 'on');
        $('#lightsStatus').attr('src', onImage);
    }
}

function blindMode() {
    var articleBody = $('#article-body');
    var currentStatus = $('#blindStatus').attr('data-status');
    var windowWidth = document.documentElement.clientWidth;
    if (currentStatus == 'off') {
        // turn on. On phones set font-size to 16px (<480 units), on desktop set font-size to 13px
        if (windowWidth < 480) {
            articleBody.animate({
                fontSize: '15px'
              }, 100);             
        } else {
            articleBody.animate({
                fontSize: '13px'
              }, 100);
           
        }
        $('#blindStatus').attr('data-status', 'on');
        $('#blindStatus').attr('src', onImage);

        // we will allow blind mode to persist across pages, in local storage
        localStorage.setItem('blindMode', 'on');
    } else {
        // turn off. Phones - 12px, Desktop - 11px
        if (windowWidth < 480) {
            articleBody.animate({
                fontSize: '13px'
            }, 100);
        } else {
            articleBody.animate({
                fontSize: '11px'
            }, 100);
        }
        $('#blindStatus').attr('data-status', 'off');
        $('#blindStatus').attr('src', offImage);

        localStorage.setItem('blindMode', 'off');
    }
}

// if localStorage has blindMode set to on, then turn on blindMode
var blindModeStatus = localStorage.getItem('blindMode');
console.log(blindModeStatus);
if (blindModeStatus == 'on') {
    blindMode();
}

var allInputElementsOnPage = $('input');

// If lights are off, then on hover on sidebar .children(), fadeTo 1 for currently hovered child
$('#sidebar').children().hover(function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on') {
        $(this).fadeTo('fast', 0.85);
    }
}, function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    // if none of the input elements are focused, then fadeTo 0.2
    if (currentStatus == 'on' && allInputElementsOnPage.is(':focus') == false) {
        $(this).fadeTo('fast', 0.2);
    }
});

// same for header and footer
$('#header').hover(function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on') {
        $(this).fadeTo('fast', 0.85);
    }
}, function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on' && allInputElementsOnPage.is(':focus') == false) {
        $(this).fadeTo('fast', 0.2);
    }
});

$('#search-form > input[type=text]').blur(function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on') {
        var isHovered = $('#header').is(':hover');
        if (isHovered == false) {
            $('#header').fadeTo('fast', 0.2);
        }
    }
});

$('#login-form > input').blur(function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on') {
        var isHovered = $('#login-area').is(':hover');
        if (isHovered == false) {
            $('#login-area').fadeTo('fast', 0.2);
        }
    }
});

$('#footer').hover(function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on') {
        $(this).fadeTo('fast', 0.85);
    }
}, function() {
    var currentStatus = $('#lightsStatus').attr('data-status');
    if (currentStatus == 'on') {
        $(this).fadeTo('fast', 0.2);
    }
});


