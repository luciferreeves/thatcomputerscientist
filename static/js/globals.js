window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

gtag("config", "G-72XTC500FR");

function changeLang(lang) {
  var date = new Date();
  date.setTime(date.getTime() + (30 * 24 * 60 * 60 * 1000)); // 30 days
  var expires = "expires=" + date.toUTCString();

  // Set the cookie
  document.cookie = "site_language=" + lang + ";" + expires + ";path=/";

  // Debugging: Print cookie value
  console.log("Cookie set: site_language=" + lang);

  // Reload the page to apply the new language
  location.reload();
}


function copyToClipboard(text) {
  $("body").append(
    '<input type="text" value="' + text + '" id="copyToClipboard">'
  );
  const copyText = $("#copyToClipboard");
  copyText.select();
  copyText[0].setSelectionRange(0, 99999);
  navigator.clipboard.writeText(copyText.val()).then(
    function () {
      alert("Copied to clipboard!");
    },
    function (err) {
      alert("Failed to copy to clipboard!");
    }
  );
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
