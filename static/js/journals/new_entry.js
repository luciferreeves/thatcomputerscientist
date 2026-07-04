(function() {
    initCustomSelects();
    initFileInputs();
    var config = JSON.parse(document.getElementById('new-entry-config').textContent);

    var editor = new FancyMiku('#editor-container', {
        height: '600px',
        placeholder: config.placeholder
    });

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
        var newCharCount = 0;

        function addNewCharacter() {
            var name = charNameInput.value.trim();
            if (!name) return;

            newCharCount++;
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

    document.getElementById('entry-form').addEventListener('submit', function(e) {
        var content = editor.getContent();
        document.getElementById('entry-content').value = content;

        if (!content || content.trim() === '<p><br></p>' || content.trim() === '') {
            e.preventDefault();
            alert(config.alertEmpty);
            return false;
        }
    });
})();
