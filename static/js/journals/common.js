function generateSlug(text, maxLength = 50) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '')
        .substring(0, maxLength);
}

function initDropdowns() {
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('dropdown-trigger') || e.target.closest('.dropdown-trigger')) {
            e.preventDefault();
            const dropdown = e.target.closest('.dropdown');
            const content = dropdown.querySelector('.dropdown-content');

            document.querySelectorAll('.dropdown-content').forEach(function (dc) {
                if (dc !== content) {
                    dc.classList.remove('show');
                }
            });

            content.classList.toggle('show');
        } else if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-content').forEach(function (dc) {
                dc.classList.remove('show');
            });
        }
    });
}

function initCustomSelects() {
    document.querySelectorAll("select.form-input").forEach(function (select) {
        if (select.dataset.customized) return;
        select.dataset.customized = "true";

        var wrapper = document.createElement("div");
        wrapper.className = "custom-select";

        var trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "custom-select-trigger";

        var selectedOption = select.options[select.selectedIndex];
        trigger.textContent = selectedOption ? selectedOption.textContent : "";
        if (!select.value) trigger.classList.add("placeholder");

        var panel = document.createElement("div");
        panel.className = "custom-select-panel";

        var search = document.createElement("input");
        search.type = "text";
        search.className = "custom-select-search";
        search.placeholder = "Search...";
        search.autocomplete = "off";

        var list = document.createElement("div");
        list.className = "custom-select-list";

        for (var i = 0; i < select.options.length; i++) {
            var opt = select.options[i];
            var item = document.createElement("button");
            item.type = "button";
            item.className = "custom-select-item";
            item.dataset.value = opt.value;
            item.textContent = opt.textContent;
            if (opt.value === select.value) item.classList.add("selected");
            if (!opt.value) item.classList.add("empty-option");
            list.appendChild(item);
        }

        if (select.options.length > 6) {
            panel.appendChild(search);
        }
        panel.appendChild(list);

        select.style.display = "none";
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(trigger);
        wrapper.appendChild(panel);
        wrapper.appendChild(select);

        trigger.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            closeAllSelects(wrapper);
            wrapper.classList.toggle("open");
            if (wrapper.classList.contains("open") && search.parentNode) {
                search.value = "";
                search.focus();
                filterItems(list, "");
            }
        });

        search.addEventListener("input", function () {
            filterItems(list, this.value);
        });

        search.addEventListener("click", function (e) {
            e.stopPropagation();
        });

        list.addEventListener("click", function (e) {
            var item = e.target.closest(".custom-select-item");
            if (!item) return;
            select.value = item.dataset.value;
            select.dispatchEvent(new Event("change", { bubbles: true }));
            trigger.textContent = item.textContent;
            trigger.classList.toggle("placeholder", !item.dataset.value);
            list.querySelectorAll(".custom-select-item").forEach(function (el) {
                el.classList.remove("selected");
            });
            item.classList.add("selected");
            wrapper.classList.remove("open");
        });
    });

    document.addEventListener("click", function (e) {
        if (!e.target.closest(".custom-select")) {
            closeAllSelects();
        }
    });
}

function closeAllSelects(except) {
    document.querySelectorAll(".custom-select.open").forEach(function (el) {
        if (el !== except) el.classList.remove("open");
    });
}

function filterItems(list, query) {
    var q = query.toLowerCase();
    list.querySelectorAll(".custom-select-item").forEach(function (item) {
        var match = item.textContent.toLowerCase().indexOf(q) !== -1;
        item.style.display = match ? "" : "none";
    });
}

function initFileInputs() {
    document.querySelectorAll('input[type="file"].form-input').forEach(function (input) {
        if (input.dataset.customized) return;
        input.dataset.customized = "true";

        var wrapper = document.createElement("div");
        wrapper.className = "file-input-wrapper";

        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "file-input-btn";
        btn.textContent = "Choose File";

        var nameSpan = document.createElement("span");
        nameSpan.className = "file-input-name";
        nameSpan.textContent = "No file chosen";

        var preview = document.createElement("img");
        preview.className = "file-input-preview";

        var clearBtn = document.createElement("button");
        clearBtn.type = "button";
        clearBtn.className = "file-input-clear";
        clearBtn.textContent = "\u00d7";

        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(btn);
        wrapper.appendChild(nameSpan);
        wrapper.appendChild(preview);
        wrapper.appendChild(clearBtn);
        wrapper.appendChild(input);

        btn.addEventListener("click", function () {
            input.click();
        });

        nameSpan.addEventListener("click", function () {
            input.click();
        });

        input.addEventListener("change", function () {
            if (input.files && input.files.length > 0) {
                var file = input.files[0];
                nameSpan.textContent = file.name;
                nameSpan.classList.add("has-file");
                clearBtn.classList.add("visible");

                if (file.type.startsWith("image/")) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        preview.src = e.target.result;
                        preview.classList.add("visible");
                    };
                    reader.readAsDataURL(file);
                } else {
                    preview.classList.remove("visible");
                    preview.src = "";
                }
            } else {
                nameSpan.textContent = "No file chosen";
                nameSpan.classList.remove("has-file");
                clearBtn.classList.remove("visible");
                preview.classList.remove("visible");
                preview.src = "";
            }
        });

        clearBtn.addEventListener("click", function () {
            input.value = "";
            input.dispatchEvent(new Event("change", { bubbles: true }));
        });
    });
}

function showErrorMessage(message) {
    const existingMessages = document.querySelector('.form-messages');
    if (existingMessages) {
        existingMessages.remove();
    }

    const messagesDiv = document.createElement('div');
    messagesDiv.className = 'form-messages';
    messagesDiv.innerHTML = `
        <div class="form-message error">
            <span class="message-icon">⚠️</span>
            <span class="message-text">${message}</span>
        </div>
    `;

    const settingsMain = document.querySelector('.settings-main');
    settingsMain.insertBefore(messagesDiv, settingsMain.firstChild);
    messagesDiv.scrollIntoView({ behavior: 'smooth' });
}