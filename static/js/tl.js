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

function restoreLang() {
  localStorage.setItem("lang", "en");
  $('#tl_ja').hide();
  $('#tl_en').show();
  var translateContainers = $('iframe');
  if (translateContainers.length === 0) {
    // nothing
  } else {
    translateContainers.each(function (index, element) {
      if (element.contentWindow.document.getElementById(":1.restore")) {
        console.log(element.contentWindow.document.getElementById(":1.restore"));
        element.contentWindow.document.getElementById(":1.restore").click();
      }
    });
  }
}

function translateJapanese() {
  localStorage.setItem("lang", "ja");
  $('#tl_en').hide();
  $('#tl_ja').show();
  var selectEl = document.querySelector("select.goog-te-combo");
  console.log(selectEl);
  if (!selectEl) {
    setTimeout(function () {
      translateJapanese();
    }, 10);
  } else if (!selectEl.options || selectEl.options.length === 0) {
    setTimeout(function () {
      translateJapanese();
    }, 10);
  } else {
    selectEl.value = 'ja';
    selectEl.dispatchEvent(new Event("change"));
  }
}

// init
var currentLang = localStorage.getItem("lang");
if (!currentLang) {
  currentLang = "en";
  localStorage.setItem("lang", "en");
}
if (currentLang === "ja") {
  $('#tl_en').hide();
  $('#tl_ja').show();
} else {
  $('#tl_ja').hide();
  $('#tl_en').show();
  restoreLang();
}
