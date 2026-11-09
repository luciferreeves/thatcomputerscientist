(function () {
    function sync(privateBox, sharedRow) {
        sharedRow.style.display = privateBox.checked ? "" : "none";
    }

    document.addEventListener("DOMContentLoaded", function () {
        var privateBox = document.getElementById("id_private");
        var sharedRow = document.querySelector(".field-shared_with");
        if (!privateBox || !sharedRow) {
            return;
        }
        privateBox.addEventListener("change", function () {
            sync(privateBox, sharedRow);
        });
        sync(privateBox, sharedRow);
    });
})();
