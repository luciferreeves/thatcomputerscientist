function savePageToDB(entirePage, path) {
    window.sessionStorage.setItem(path, entirePage);
    // db.collection('pages').doc(path).set({ path: path, page: entirePage });
}

const lang = localStorage.getItem("lang");
const path = window.location.pathname;

const storedPage = window.sessionStorage.getItem(path);

if (lang === "ja" && storedPage) {
    console.log("Page already translated");
    document.getElementById('wrap').innerHTML = storedPage;
} else {
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src =
        "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    document.getElementById("tl_block").appendChild(script);
}
