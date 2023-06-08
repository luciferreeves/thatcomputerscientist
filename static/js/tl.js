// Google Translate (Only English and Japanese)
function googleTranslateElementInit() {
  new google.translate.TranslateElement(
    {
      pageLanguage: "en",
      includedLanguages: "ja",
    },
    "google_translate_element"
  );
}

var currentLang = document.cookie.replace(
  /(?:(?:^|.*;\s*)lang\s*\=\s*([^;]*).*$)|^.*$/,
  "$1"
);

if (currentLang == "ja") {
  triggerTranslation("ja");
} else {
  triggerTranslation("en");
}

function triggerTranslation(language) {
  var selectEl = document.querySelector("select.goog-te-combo");
  if (!selectEl) {
    setTimeout(function () {
      triggerTranslation(language);
    }, 10);
  } else if (!selectEl.options || selectEl.options.length === 0) {
    setTimeout(function () {
      triggerTranslation(language);
    }, 10);
  } else {
    selectEl.value = language;
    selectEl.dispatchEvent(new Event("change"));
    // visiblity of #main-section is hidden until translation is done, show it after translation is done
    document.getElementById("main-section").style.visibility = "visible";
  }
}
