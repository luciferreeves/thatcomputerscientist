let translationCounter = 0;
let editor = null;

function updateLanguageDropdowns() {
    const allSelects = document.querySelectorAll('select[name^="translation_language_"]');
    const selectedLanguages = new Set();

    allSelects.forEach(select => {
        if (select.value && select.closest('.translation-row').style.display !== 'none') {
            selectedLanguages.add(select.value);
        }
    });

    allSelects.forEach(select => {
        const currentValue = select.value;
        Array.from(select.options).forEach(option => {
            if (option.value && option.value !== currentValue) {
                option.disabled = selectedLanguages.has(option.value);
            }
        });
    });
}

function initTranslationManagement() {
    const addTranslationBtn = document.getElementById('add-translation-btn');
    if (addTranslationBtn) {
        addTranslationBtn.addEventListener('click', function () {
            const container = document.querySelector('.translations-container');
            const existingSelect = document.querySelector('select[name^="translation_language_"]');
            const languageOptions = existingSelect ?
                Array.from(existingSelect.options)
                    .map(option => `<option value="${option.value}">${option.textContent}</option>`)
                    .join('') : '';

            const newRow = document.createElement('div');
            newRow.className = 'journal-card translation-row';
            newRow.innerHTML = `
                <div class="translation-fields">
                    <select name="translation_language_new_${translationCounter}" class="form-input">
                        <option value="">Select Language</option>
                        ${languageOptions}
                    </select>
                    <input type="text" 
                           name="translation_name_new_${translationCounter}" 
                           class="form-input" 
                           placeholder="Name">
                    <textarea name="translation_description_new_${translationCounter}" 
                              class="form-textarea" 
                              rows="2"
                              placeholder="Description"></textarea>
                    <button type="button" class="action-btn remove-translation-btn">×</button>
                </div>
            `;

            container.appendChild(newRow);
            translationCounter++;
            updateLanguageDropdowns();
        });
    }

    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-translation-btn')) {
            const row = e.target.closest('.translation-row');
            const select = row.querySelector('select[name^="translation_language_"]');

            if (select.name.includes('_new_')) {
                row.remove();
            } else {
                const translationId = select.name.replace('translation_language_', '');
                const deleteInput = document.createElement('input');
                deleteInput.type = 'hidden';
                deleteInput.name = `delete_translation_${translationId}`;
                deleteInput.value = 'true';
                row.appendChild(deleteInput);
                row.style.display = 'none';
            }
            updateLanguageDropdowns();
        }
    });

    document.addEventListener('change', function (e) {
        if (e.target.name && e.target.name.startsWith('translation_language_')) {
            updateLanguageDropdowns();
        }
    });
}

function initUserSharing() {
    const addUserBtn = document.getElementById('add-user-btn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function () {
            const input = document.getElementById('shared_users');
            const username = input.value.trim();

            if (!username) {
                return;
            }

            const existingUsers = Array.from(document.querySelectorAll('.user-badge')).map(badge =>
                badge.textContent.trim().replace('×', '').trim()
            );

            if (existingUsers.includes(username)) {
                input.value = '';
                return;
            }

            const usersList = document.querySelector('.shared-users-list');
            const userBadge = document.createElement('span');
            userBadge.className = 'user-badge';
            userBadge.innerHTML = `
                ${username} 
                <button type="button" class="remove-user-btn" data-username="${username}">×</button>
                <input type="hidden" name="add_shared_user" value="${username}">
            `;
            usersList.appendChild(userBadge);
            input.value = '';
        });
    }

    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-user-btn')) {
            e.target.closest('.user-badge').remove();
        }
    });
}

async function validateCSS(css) {
    if (!css.trim()) return { valid: true, errors: [] };

    try {
        const formData = new FormData();
        formData.append('text', css);
        formData.append('output', 'json');
        formData.append('profile', 'css3svg');

        const response = await fetch('https://jigsaw.w3.org/css-validator/validator', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        console.log(result)

        if (result.cssvalidation && result.cssvalidation.errors && result.cssvalidation.errors.length > 0) {
            const errors = result.cssvalidation.errors.map(error =>
                `Line ${error.line}: ${error.message}`
            );
            return { valid: false, errors };
        }

        return { valid: true, errors: [] };
    } catch (error) {
        return { valid: true, errors: [] };
    }
}

function initCodeMirror() {
    editor = CodeMirror(document.getElementById('code-editor'), {
        value: document.getElementById('custom_css').value,
        mode: 'css',
        theme: 'vintage',
        lineNumbers: true,
        lineWrapping: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        autoCloseBrackets: true,
        showHint: true,
        hintOptions: {
            completeSingle: false,
        },
        extraKeys: {
            'Ctrl-/': 'toggleComment',
            'Cmd-/': 'toggleComment',
            'Ctrl-Space': 'autocomplete',
            'Cmd-Space': 'autocomplete',
            'Tab': function (cm) {
                if (cm.somethingSelected()) {
                    cm.indentSelection('add');
                } else {
                    cm.replaceSelection('    ', 'end');
                }
            }
        }
    });

    editor.on('inputRead', function (cm, change) {
        if (change.text[0] && /[a-zA-Z]/.test(change.text[0])) {
            cm.showHint();
        }
    });

    editor.on('change', function () {
        document.getElementById('custom_css').value = editor.getValue();
    });
}

function initFormSubmission() {
    const form = document.querySelector('form.form-container');
    if (form) {
        form.addEventListener('submit', async function (e) {
            const cssValue = editor.getValue();
            document.getElementById('custom_css').value = cssValue;

            if (cssValue.trim()) {
                e.preventDefault();

                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;

                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="validation-spinner"></span>Validating CSS...';

                const validation = await validateCSS(cssValue);

                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;

                if (!validation.valid) {
                    showErrorMessage('CSS Validation Errors:<br><br>' + validation.errors.join('<br>'));
                    return false;
                } else {
                    form.submit();
                }
            }
        });
    }
}

function initSettingsSlugGeneration() {
    const journalNameInput = document.querySelector('input[name="name"]');
    const journalSlugInput = document.querySelector('input[name="slug"]');

    if (journalNameInput && journalSlugInput) {
        journalNameInput.addEventListener('input', function () {
            if (!journalSlugInput.value || journalSlugInput.dataset.autoGenerated === 'true') {
                const slug = generateSlug(this.value);
                journalSlugInput.value = slug;
                journalSlugInput.dataset.autoGenerated = 'true';
            }
        });

        journalSlugInput.addEventListener('input', function () {
            this.dataset.autoGenerated = 'false';
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    updateLanguageDropdowns();
    initTranslationManagement();
    initUserSharing();
    initCodeMirror();
    initFormSubmission();
    initSettingsSlugGeneration();
});