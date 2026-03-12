(function() {
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
})();
