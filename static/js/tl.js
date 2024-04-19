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
  $('body').addClass('en');
  $('body').removeClass('ja');
  var translateContainers = $('iframe');
  if (translateContainers.length === 0) {
    // nothing
  } else {
    translateContainers.each(function (index, element) {
      if (element.contentWindow.document.getElementById(":1.close")) {
        element.contentWindow.document.getElementById(":1.close").click();
      }
    });
  }
}

function translateJapanese() {
  localStorage.setItem("lang", "ja");
  $('#tl_en').hide();
  $('#tl_ja').show();
  $('body').addClass('ja');
  $('body').removeClass('en');
  var selectEl = document.querySelector("select.goog-te-combo");
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
    setTimeout(function () {
      save();
    }, 6969);
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
  $('body').addClass('ja');
  $('body').removeClass('en');
  setTimeout(function () {
    save();
  }, 6969);
} else {
  $('#tl_ja').hide();
  $('#tl_en').show();
  $('body').addClass('en');
  $('body').removeClass('ja');
  restoreLang();
}

// let entirePage;

function save() {
  // only body
  const entirePage = document.getElementById('wrap').innerHTML;
  const path = window.location.pathname;
  
  const storedPage = window.sessionStorage.getItem(path);

  if (storedPage === null || storedPage !== entirePage) {
    console.log('Saving page to DB');
    window.sessionStorage.setItem(path, entirePage);
  }

  // db.collection('pages').doc(path).get().then(page => {
  //   const storedPage = page?.page;
  //   if (storedPage === null || storedPage !== entirePage) {
  //     console.log('Saving page to DB');
  //     savePageToDB(entirePage, path);
  //   }
  // });
}
