/**
 * Phone compatibility JS, for handling things on phone as 
 * this site was written for desktop
 */

const windowBreakpoint = 450;

// Listen for window resize
$(window).resize(function() {
    if($(window).width() > windowBreakpoint) {
        $('#sidebar').css('display', 'block');
        $('#ハンバーガー').css('display', 'none');
    } else {
        $('#sidebar').css('display', 'none');
        $('#ハンバーガー').css('display', 'block');
    }
});

$(document).ready(function() {
    $('#ハンバーガー').click(function() {
        $('#ham').toggleClass('open');
        if($('#sidebar').css('display') == 'none') {
            $('#sidebar').css('display', 'block');
            $('body').css('overflow', 'hidden');
            $('#ハンバーガー').css('background-color', 'red');

        } else {
            $('#sidebar').css('display', 'none');
            $('body').css('overflow', 'auto');
            $('#ハンバーガー').css('background-color', 'transparent');
        }
    });
});