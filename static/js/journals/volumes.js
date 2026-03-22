document.addEventListener("DOMContentLoaded", function () {
    initDropdowns();
    initCustomSelects();
    initFileInputs();

    var toggleBtn = document.getElementById("toggle-volume-form");
    var form = document.getElementById("volume-form");
    var cancelBtn = document.getElementById("cancel-volume-form");

    if (toggleBtn && form) {
        toggleBtn.addEventListener("click", function () {
            form.classList.toggle("hidden");
            form.querySelector("input[name='volume_id']")?.remove();
        });
    }

    if (cancelBtn && form) {
        cancelBtn.addEventListener("click", function () {
            form.classList.add("hidden");
            form.querySelector("form").reset();
            form.querySelector("input[name='volume_id']")?.remove();
        });
    }

    var coverPreview = document.getElementById("volume-cover-preview");
    var coverImg = document.getElementById("volume-cover-img");
    var coverHint = document.getElementById("volume-cover-hint");

    document.querySelectorAll(".edit-volume-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (!form) return;
            form.classList.remove("hidden");

            var existing = form.querySelector("input[name='volume_id']");
            if (!existing) {
                var input = document.createElement("input");
                input.type = "hidden";
                input.name = "volume_id";
                form.querySelector("form").appendChild(input);
                existing = input;
            }
            existing.value = btn.dataset.id;

            form.querySelector("#volume-title").value = btn.dataset.title || "";
            form.querySelector("#volume-description").value = btn.dataset.description || "";

            if (btn.dataset.cover && coverPreview && coverImg) {
                coverImg.src = btn.dataset.cover;
                coverPreview.classList.remove("hidden");
                coverHint.textContent = "Upload a new image to replace the current cover";
            } else if (coverPreview) {
                coverPreview.classList.add("hidden");
                coverHint.textContent = "";
            }

            form.scrollIntoView({ behavior: "smooth" });
        });
    });

    if (toggleBtn && coverPreview) {
        toggleBtn.addEventListener("click", function () {
            coverPreview.classList.add("hidden");
            if (coverHint) coverHint.textContent = "";
        });
    }
    if (cancelBtn && coverPreview) {
        cancelBtn.addEventListener("click", function () {
            coverPreview.classList.add("hidden");
            if (coverHint) coverHint.textContent = "";
        });
    }

    var list = document.getElementById("volume-list");
    var reorderActions = document.getElementById("reorder-actions");
    var cancelReorder = document.getElementById("cancel-reorder");

    if (!list) return;

    var dragItem = null;
    var placeholder = null;
    var originalOrder = [];

    function captureOrder() {
        originalOrder = [];
        list.querySelectorAll(".draggable-item").forEach(function (item) {
            originalOrder.push(item.dataset.id);
        });
    }

    function getCurrentOrder() {
        var order = [];
        list.querySelectorAll(".draggable-item").forEach(function (item) {
            order.push(item.dataset.id);
        });
        return order;
    }

    function updateHiddenInputs() {
        list.querySelectorAll(".draggable-item").forEach(function (item) {
            var input = item.querySelector("input[name='volume_order']");
            if (input) input.value = item.dataset.id;
        });
    }

    function checkOrderChanged() {
        var current = getCurrentOrder();
        var changed = false;
        for (var i = 0; i < current.length; i++) {
            if (current[i] !== originalOrder[i]) {
                changed = true;
                break;
            }
        }
        if (reorderActions) {
            reorderActions.classList.toggle("hidden", !changed);
        }
    }

    captureOrder();

    list.addEventListener("mousedown", function (e) {
        var handle = e.target.closest(".drag-handle");
        if (!handle) return;
        e.preventDefault();

        dragItem = handle.closest(".draggable-item");
        if (!dragItem) return;

        var rect = dragItem.getBoundingClientRect();
        dragItem.classList.add("dragging");
        dragItem.style.width = rect.width + "px";

        placeholder = document.createElement("div");
        placeholder.className = "drag-placeholder";
        placeholder.style.height = rect.height + "px";
        list.insertBefore(placeholder, dragItem);

        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
    });

    function onMouseMove(e) {
        if (!dragItem || !placeholder) return;

        var items = list.querySelectorAll(".draggable-item:not(.dragging)");
        var inserted = false;

        for (var i = 0; i < items.length; i++) {
            var rect = items[i].getBoundingClientRect();
            var midY = rect.top + rect.height / 2;

            if (e.clientY < midY) {
                list.insertBefore(placeholder, items[i]);
                inserted = true;
                break;
            }
        }

        if (!inserted) {
            list.appendChild(placeholder);
        }
    }

    function onMouseUp() {
        if (!dragItem || !placeholder) return;

        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);

        list.insertBefore(dragItem, placeholder);
        placeholder.remove();
        placeholder = null;

        dragItem.classList.remove("dragging");
        dragItem.style.width = "";
        dragItem = null;

        updateHiddenInputs();
        checkOrderChanged();
    }

    if (cancelReorder) {
        cancelReorder.addEventListener("click", function () {
            originalOrder.forEach(function (id) {
                var item = list.querySelector('.draggable-item[data-id="' + id + '"]');
                if (item) list.appendChild(item);
            });
            updateHiddenInputs();
            checkOrderChanged();
        });
    }
});
