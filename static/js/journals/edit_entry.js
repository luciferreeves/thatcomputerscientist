(function() {
    initCustomSelects();
    initFileInputs();
    var config = JSON.parse(document.getElementById('edit-entry-config').textContent);
    var editors = {};
    var tabsContainer = document.getElementById('edit-tabs');
    var addWrapper = document.getElementById('add-lang-wrapper');
    var langDropdown = document.getElementById('lang-dropdown');
    var form = document.getElementById('entry-form');

    editors['main'] = new FancyMiku('#editor-main', {
        height: '600px',
        placeholder: config.placeholderMain
    });
    editors['main'].setContent(config.mainContent);

    config.translations.forEach(function(t) {
        var key = 'lang-' + t.id;
        editors[key] = new FancyMiku('#editor-lang-' + t.id, {
            height: '600px',
            placeholder: config.placeholderTranslation
        });
        editors[key].setContent(t.content);
    });

    function switchTab(tabId) {
        tabsContainer.querySelectorAll('.edit-tab').forEach(function(t) { t.classList.remove('active'); });
        document.querySelectorAll('.edit-tab-content').forEach(function(c) { c.classList.remove('active'); });

        var tabBtn = tabsContainer.querySelector('.edit-tab[data-tab="' + tabId + '"]');
        var tabContent = document.getElementById('tab-' + tabId);

        if (tabBtn) tabBtn.classList.add('active');
        if (tabContent) tabContent.classList.add('active');
    }

    tabsContainer.addEventListener('click', function(e) {
        var closeBtn = e.target.closest('.tab-close');
        if (closeBtn) {
            e.stopPropagation();
            removeTranslationTab(closeBtn.closest('.edit-tab'));
            return;
        }

        if (e.target.closest('#add-lang-btn')) {
            updateLangDropdown();
            langDropdown.classList.toggle('show');
            return;
        }

        var dropdownItem = e.target.closest('.edit-lang-dropdown-item');
        if (dropdownItem) {
            addLanguageTab(dropdownItem.dataset.langCode, dropdownItem.dataset.langName);
            return;
        }

        var tab = e.target.closest('.edit-tab[data-tab]');
        if (tab) {
            switchTab(tab.dataset.tab);
        }
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('#add-lang-wrapper')) {
            langDropdown.classList.remove('show');
        }
    });

    function removeTranslationTab(tab) {
        var tabId = tab.dataset.tab;
        var content = document.getElementById('tab-' + tabId);

        var prevTab = tab.previousElementSibling;
        while (prevTab && !prevTab.dataset.tab) {
            prevTab = prevTab.previousElementSibling;
        }
        var switchTo = prevTab ? prevTab.dataset.tab : 'main';

        var deleteFlag = content ? content.querySelector('.delete-flag') : null;
        if (deleteFlag) {
            deleteFlag.disabled = false;
            deleteFlag.value = 'true';
        }

        tab.remove();
        if (content) content.remove();
        if (editors[tabId]) delete editors[tabId];

        switchTab(switchTo);
        updateLangDropdown();
    }

    function addLanguageTab(code, name) {
        var id = 'new_' + Date.now();

        var tabBtn = document.createElement('button');
        tabBtn.type = 'button';
        tabBtn.className = 'edit-tab lang-tab';
        tabBtn.dataset.tab = 'lang-' + id;
        tabBtn.dataset.lang = code;
        tabBtn.innerHTML = name + ' <span class="tab-close" title="' + config.labelRemoveTranslation + '">×</span>';

        tabsContainer.insertBefore(tabBtn, addWrapper);

        var tabContent = document.createElement('div');
        tabContent.className = 'edit-tab-content';
        tabContent.id = 'tab-lang-' + id;
        tabContent.dataset.lang = code;
        tabContent.innerHTML =
            '<input type="hidden" name="translation_language_new_' + id + '" value="' + code + '" class="translation-lang-input" />' +
            '<div class="form-group">' +
                '<label class="form-label">' + config.labelTranslatedTitle + '</label>' +
                '<input type="text" name="translation_title_new_' + id + '" class="form-input" placeholder="' + config.labelTranslatedTitle + '" />' +
            '</div>' +
            '<div class="form-group">' +
                '<label class="form-label">' + config.labelTranslatedContent + '</label>' +
                '<div id="editor-lang-' + id + '" class="translation-editor"></div>' +
                '<input type="hidden" id="content-lang-' + id + '" name="translation_content_new_' + id + '" />' +
            '</div>';

        form.insertBefore(tabContent, document.getElementById('tab-settings'));

        editors['lang-' + id] = new FancyMiku('#editor-lang-' + id, {
            height: '600px',
            placeholder: config.placeholderTranslation
        });

        langDropdown.classList.remove('show');
        switchTab('lang-' + id);
        updateLangDropdown();
    }

    function getUsedLanguages() {
        var used = new Set(['en']);
        tabsContainer.querySelectorAll('.edit-tab.lang-tab').forEach(function(tab) {
            if (tab.dataset.lang) used.add(tab.dataset.lang);
        });
        return used;
    }

    function updateLangDropdown() {
        var used = getUsedLanguages();
        langDropdown.querySelectorAll('.edit-lang-dropdown-item').forEach(function(item) {
            item.style.display = used.has(item.dataset.langCode) ? 'none' : '';
        });
    }

    form.addEventListener('submit', function(e) {
        var mainContent = editors['main'].getContent();
        document.getElementById('content-main').value = mainContent;

        if (!mainContent || mainContent.trim() === '<p><br></p>' || mainContent.trim() === '') {
            e.preventDefault();
            alert(config.alertEmptyContent);
            return false;
        }

        for (var key in editors) {
            if (key === 'main') continue;
            var hiddenInput = document.getElementById('content-' + key);
            if (hiddenInput) {
                hiddenInput.value = editors[key].getContent();
            }
        }
    });

    document.getElementById('delete-entry-btn').addEventListener('click', function() {
        if (confirm(config.confirmDelete)) {
            window.location.href = config.deleteUrl;
        }
    });

    updateLangDropdown();

    var addCharBtn = document.getElementById('add-character-btn');
    var toggleQuickChar = document.getElementById('toggle-quick-character');
    var quickCharForm = document.getElementById('quick-character-form');
    var cancelQuickChar = document.getElementById('cancel-quick-character');
    var charNameInput = document.getElementById('new-character-name');
    var charRoleInput = document.getElementById('new-character-role');
    var charBioInput = document.getElementById('new-character-bio');
    var charPicker = document.getElementById('characters-picker');

    if (toggleQuickChar && quickCharForm) {
        toggleQuickChar.addEventListener('click', function() {
            quickCharForm.classList.toggle('hidden');
        });
        if (cancelQuickChar) {
            cancelQuickChar.addEventListener('click', function() {
                quickCharForm.classList.add('hidden');
                charNameInput.value = '';
                if (charBioInput) charBioInput.value = '';
            });
        }
    }

    if (addCharBtn && charNameInput && charPicker) {
        function addNewCharacter() {
            var name = charNameInput.value.trim();
            if (!name) return;

            var role = charRoleInput ? charRoleInput.value : 'Supporting';
            var bio = charBioInput ? charBioInput.value.trim() : '';

            var label = document.createElement('label');
            label.className = 'tag-pick';
            label.innerHTML =
                '<input type="checkbox" name="new_character_names" value="' + name.replace(/"/g, '&quot;') + '" checked />' +
                '<input type="hidden" name="new_character_roles" value="' + role.replace(/"/g, '&quot;') + '" />' +
                '<input type="hidden" name="new_character_bios" value="' + bio.replace(/"/g, '&quot;') + '" />' +
                '<span class="tag-pick-label">' + name + ' <small>(' + role + ')</small></span>';
            charPicker.appendChild(label);

            charNameInput.value = '';
            if (charBioInput) charBioInput.value = '';
            quickCharForm.classList.add('hidden');
        }

        addCharBtn.addEventListener('click', addNewCharacter);
    }

    var toggleQuickTag = document.getElementById('toggle-quick-tag');
    var quickTagForm = document.getElementById('quick-tag-form');
    var cancelQuickTag = document.getElementById('cancel-quick-tag');
    var addTagBtn = document.getElementById('add-tag-btn');
    var tagNameInput = document.getElementById('new-tag-name');
    var tagsPicker = document.getElementById('tags-picker');

    if (toggleQuickTag && quickTagForm) {
        toggleQuickTag.addEventListener('click', function() {
            quickTagForm.classList.toggle('hidden');
        });
        if (cancelQuickTag) {
            cancelQuickTag.addEventListener('click', function() {
                quickTagForm.classList.add('hidden');
                tagNameInput.value = '';
            });
        }
    }

    if (addTagBtn && tagNameInput && tagsPicker) {
        function addNewTag() {
            var name = tagNameInput.value.trim();
            if (!name) return;
            var nameLower = name.toLowerCase();

            var existing = tagsPicker.querySelectorAll('.tag-pick');
            for (var i = 0; i < existing.length; i++) {
                var label = existing[i].querySelector('.tag-pick-label');
                if (label && label.textContent.trim().toLowerCase() === nameLower) {
                    existing[i].querySelector('input[type="checkbox"]').checked = true;
                    tagNameInput.value = '';
                    quickTagForm.classList.add('hidden');
                    return;
                }
            }

            var el = document.createElement('label');
            el.className = 'tag-pick';
            el.innerHTML =
                '<input type="checkbox" name="new_tag_names" value="' + name.replace(/"/g, '&quot;') + '" checked />' +
                '<span class="tag-pick-label">' + name + '</span>';
            tagsPicker.appendChild(el);

            tagNameInput.value = '';
            quickTagForm.classList.add('hidden');
        }

        addTagBtn.addEventListener('click', addNewTag);
        tagNameInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { e.preventDefault(); addNewTag(); }
        });
    }
})();
