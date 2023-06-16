window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

gtag("config", "G-72XTC500FR");

function changeLang(lang) {
  if (lang === "ja") {
    translateJapanese();
  } else {
    restoreLang();
  }
}

function copyToClipboard(text) {
  $('body').append('<input type="text" value="' + text + '" id="copyToClipboard">');
  const copyText = $('#copyToClipboard');
  copyText.select();
  copyText[0].setSelectionRange(0, 99999);
  navigator.clipboard.writeText(copyText.val()).then(function () {
    alert("Copied to clipboard!");
  }, function (err) {
    alert("Failed to copy to clipboard!");
  });
  copyText.remove();
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
