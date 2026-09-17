document.addEventListener("DOMContentLoaded", function () {
    initDropdowns();
    initCustomSelects();
    initFileInputs();

    function setupToggle(toggleId, formId, cancelId) {
        var toggleBtn = document.getElementById(toggleId);
        var form = document.getElementById(formId);
        var cancelBtn = document.getElementById(cancelId);

        if (toggleBtn && form) {
            toggleBtn.addEventListener("click", function () {
                form.classList.toggle("hidden");
            });
        }

        if (cancelBtn && form) {
            cancelBtn.addEventListener("click", function () {
                form.classList.add("hidden");
                form.querySelector("form").reset();
            });
        }
    }

    setupToggle("toggle-character-form", "character-form", "cancel-character-form");
    setupToggle("toggle-relationship-form", "relationship-form", "cancel-relationship-form");

    var fromSelect = document.getElementById("from-character");
    var toSelect = document.getElementById("to-character");
    var relForm = document.getElementById("relationship-form");

    if (relForm && fromSelect && toSelect) {
        function disableSameCharacter(changed, other) {
            var val = changed.value;
            for (var i = 0; i < other.options.length; i++) {
                other.options[i].disabled = other.options[i].value && other.options[i].value === val;
            }
            var otherWrapper = other.closest(".custom-select");
            if (otherWrapper) {
                otherWrapper.querySelectorAll(".custom-select-item").forEach(function (item) {
                    if (item.dataset.value && item.dataset.value === val) {
                        item.classList.add("disabled-option");
                    } else {
                        item.classList.remove("disabled-option");
                    }
                });
            }
        }

        fromSelect.addEventListener("change", function () { disableSameCharacter(fromSelect, toSelect); });
        toSelect.addEventListener("change", function () { disableSameCharacter(toSelect, fromSelect); });

        relForm.querySelector("form").addEventListener("submit", function (e) {
            if (fromSelect.value && fromSelect.value === toSelect.value) {
                e.preventDefault();
                alert("From and To cannot be the same character.");
            }
        });
    }

    var charForm = document.getElementById("character-form");

    document.querySelectorAll(".edit-character-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (!charForm) return;
            charForm.classList.remove("hidden");

            var existing = charForm.querySelector("input[name='character_id']");
            if (!existing) {
                var input = document.createElement("input");
                input.type = "hidden";
                input.name = "character_id";
                charForm.querySelector("form").appendChild(input);
                existing = input;
            }
            existing.value = btn.dataset.id;

            charForm.querySelector("#character-name").value = btn.dataset.name || "";

            var roleSelect = charForm.querySelector("#character-role");
            var roleValue = btn.dataset.role || "";
            roleSelect.value = roleValue;
            var roleTrigger = roleSelect.closest(".custom-select");
            if (roleTrigger) {
                var triggerBtn = roleTrigger.querySelector(".custom-select-trigger");
                var selectedOpt = roleSelect.options[roleSelect.selectedIndex];
                if (triggerBtn && selectedOpt) triggerBtn.textContent = selectedOpt.textContent;
                roleTrigger.querySelectorAll(".custom-select-item").forEach(function (item) {
                    item.classList.toggle("selected", item.dataset.value === roleValue);
                });
            }

            charForm.querySelector("#character-bio").value = btn.dataset.bio || "";
            charForm.scrollIntoView({ behavior: "smooth" });
        });
    });

    var list = document.getElementById("character-list");
    var reorderActions = document.getElementById("reorder-actions");
    var cancelReorder = document.getElementById("cancel-reorder");

    if (!list) return;

    var originalOrder = [];
    var dragSrcEl = null;

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
            var input = item.querySelector("input[name='character_order']");
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

    list.querySelectorAll(".drag-handle").forEach(function (handle) {
        var card = handle.closest(".draggable-item");
        handle.addEventListener("mousedown", function () {
            card.setAttribute("draggable", "true");
        });
    });

    document.addEventListener("mouseup", function () {
        list.querySelectorAll(".draggable-item").forEach(function (item) {
            item.removeAttribute("draggable");
        });
    });

    list.addEventListener("dragstart", function (e) {
        var item = e.target.closest(".draggable-item");
        if (!item) return;
        dragSrcEl = item;
        item.classList.add("dragging");
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", item.dataset.id);
    });

    list.addEventListener("dragover", function (e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";

        var target = e.target.closest(".draggable-item");
        if (!target || target === dragSrcEl) return;

        var rect = target.getBoundingClientRect();
        var midX = rect.left + rect.width / 2;
        var midY = rect.top + rect.height / 2;
        var after = (e.clientY > midY) || (e.clientY >= rect.top && e.clientY <= rect.bottom && e.clientX > midX);

        if (after) {
            target.parentNode.insertBefore(dragSrcEl, target.nextSibling);
        } else {
            target.parentNode.insertBefore(dragSrcEl, target);
        }
    });

    list.addEventListener("dragend", function (e) {
        var item = e.target.closest(".draggable-item");
        if (item) {
            item.classList.remove("dragging");
            item.removeAttribute("draggable");
        }
        dragSrcEl = null;
        updateHiddenInputs();
        checkOrderChanged();
    });

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
