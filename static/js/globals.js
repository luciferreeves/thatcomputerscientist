window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

gtag("config", "G-72XTC500FR");

function changeLang(lang) {
  document.cookie = "lang=" + lang + "; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";
  location.reload();
}

// Smooth scroll to anchor
$(document).ready(function () {
  $('a[href^="#"]').on("click", function (e) {
    e.preventDefault();

    const target = $(this.getAttribute("href"));
    if (target.length) {
      $("html, body").stop().animate(
        {
          scrollTop: target.offset().top,
        },
        500
      );
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  var equationElements = document.getElementsByTagName("*");

  for (var i = 0; i < equationElements.length; i++) {
    var element = equationElements[i];

    if (
      element.innerHTML.startsWith("$$") &&
      element.innerHTML.endsWith("$$")
    ) {
      element.style.overflowX = "scroll";
      element.style.whiteSpace = "nowrap";
      element.classList.add("equation-container");
    }
  }
});

function summonOneko() {
  document.cookie =
    "summonOneko=true; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";
  location.reload();
}

function withdrawOneko() {
  document.cookie =
    "summonOneko=false; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";
  location.reload();
}
