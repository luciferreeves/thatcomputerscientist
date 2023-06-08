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

console.log("currentLang: " + currentLang);

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
    }, 100);
  } else if (!selectEl.options || selectEl.options.length === 0) {
    setTimeout(function () {
      triggerTranslation(language);
    }, 100);
  } else {
    // Continue with the logic for handling the available options
    selectEl.value = language; // Change the value of the select element
    selectEl.dispatchEvent(new Event("change")); // Trigger change event
  }
}
