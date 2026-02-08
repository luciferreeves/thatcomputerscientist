(function () {
    'use strict';

    const LANGUAGES = [
        'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'csharp', 'php', 'ruby', 'go',
        'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'julia', 'perl', 'bash', 'shell',
        'powershell', 'sql', 'html', 'css', 'scss', 'less', 'xml', 'json', 'yaml', 'toml',
        'markdown', 'latex', 'dart', 'elixir', 'erlang', 'haskell', 'lua', 'objective-c',
        'fortran', 'assembly', 'vhdl', 'verilog', 'graphql', 'dockerfile', 'nginx', 'apache'
    ];

    class FancyMiku {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.options = {
                height: options.height || '500px',
                placeholder: options.placeholder || 'Start writing...',
                onChange: options.onChange || null
            };

            this.savedSelection = null;
            this.isSourceMode = false;
            this.currentPopup = null;
            this.init();
        }

        init() {
            this.container.innerHTML = '';
            this.createEditor();
            this.attachEventListeners();
        }

        createEditor() {
            const wrapper = document.createElement('div');
            wrapper.className = 'miku-container';

            const toolbar = this.createToolbar();
            wrapper.appendChild(toolbar);

            const editableArea = document.createElement('div');
            editableArea.className = 'miku-content';
            editableArea.contentEditable = 'true';
            editableArea.setAttribute('data-placeholder', this.options.placeholder);
            editableArea.style.height = this.options.height;
            editableArea.innerHTML = '<p><br></p>';
            wrapper.appendChild(editableArea);

            const sourceArea = document.createElement('textarea');
            sourceArea.className = 'miku-source';
            sourceArea.style.height = this.options.height;
            sourceArea.style.display = 'none';
            wrapper.appendChild(sourceArea);

            this.container.appendChild(wrapper);
            this.wrapper = wrapper;
            this.toolbar = toolbar;
            this.editableArea = editableArea;
            this.sourceArea = sourceArea;
        }

        createToolbar() {
            const toolbar = document.createElement('div');
            toolbar.className = 'miku-toolbar';

            const buttons = [
                { icon: 'H1', title: 'Heading 1', command: 'heading', value: 'h1' },
                { icon: 'H2', title: 'Heading 2', command: 'heading', value: 'h2' },
                { icon: 'H3', title: 'Heading 3', command: 'heading', value: 'h3' },
                { separator: true },
                { icon: '<strong>B</strong>', title: 'Bold', command: 'bold' },
                { icon: '<em>I</em>', title: 'Italic', command: 'italic' },
                { icon: '<u>U</u>', title: 'Underline', command: 'underline' },
                { icon: '<s>S</s>', title: 'Strikethrough', command: 'strikethrough' },
                { separator: true },
                { icon: '🔗', title: 'Insert Link', command: 'link' },
                { icon: '🖼️', title: 'Insert Image', command: 'image' },
                { separator: true },
                { icon: '❝❞', title: 'Blockquote', command: 'blockquote' },
                { icon: '</>', title: 'Code Block', command: 'codeblock' },
                { icon: '`', title: 'Inline Code', command: 'inlinecode' },
                { separator: true },
                { icon: '⇄', title: 'Toggle Source', command: 'togglesource', special: true }
            ];

            buttons.forEach(btn => {
                if (btn.separator) {
                    const separator = document.createElement('span');
                    separator.className = 'miku-toolbar-separator';
                    toolbar.appendChild(separator);
                } else {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'miku-btn';
                    if (btn.special) button.classList.add('miku-btn-special');
                    button.innerHTML = btn.icon;
                    button.title = btn.title;
                    button.dataset.command = btn.command;
                    if (btn.value) button.dataset.value = btn.value;
                    toolbar.appendChild(button);
                }
            });

            return toolbar;
        }

        attachEventListeners() {
            this.toolbar.addEventListener('click', (e) => {
                const btn = e.target.closest('.miku-btn');
                if (!btn) return;
                e.preventDefault();
                this.executeCommand(btn.dataset.command, btn.dataset.value);
            });

            this.editableArea.addEventListener('mouseup', () => this.saveSelection());
            this.editableArea.addEventListener('keyup', () => {
                this.saveSelection();
                this.handleLinkEditing();
            });
            this.editableArea.addEventListener('click', (e) => this.handleLinkClick(e));
            this.editableArea.addEventListener('keydown', (e) => this.handleKeyDown(e));

            this.editableArea.addEventListener('input', () => {
                this.ensureParagraphStructure();
                if (this.options.onChange) {
                    this.options.onChange(this.getContent());
                }
            });

            this.editableArea.addEventListener('paste', (e) => this.handlePaste(e));

            this.editableArea.addEventListener('blur', () => {
                if (this.editableArea.innerHTML.trim() === '') {
                    this.editableArea.innerHTML = '<p><br></p>';
                }
            });

            document.addEventListener('click', (e) => {
                if (this.currentPopup && !this.currentPopup.contains(e.target) && !e.target.closest('.miku-btn')) {
                    this.closePopup();
                }
            });
        }

        saveSelection() {
            const sel = window.getSelection();
            if (sel.rangeCount > 0) {
                this.savedSelection = sel.getRangeAt(0);
            }
        }

        restoreSelection() {
            if (this.savedSelection) {
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(this.savedSelection);
            }
        }

        executeCommand(command, value = null) {
            if (command === 'togglesource') {
                this.toggleSource();
                return;
            }

            if (this.isSourceMode) {
                alert('Switch to WYSIWYG mode to use formatting commands.');
                return;
            }

            this.restoreSelection();
            this.editableArea.focus();

            switch (command) {
                case 'heading':
                    this.formatHeading(value);
                    break;
                case 'bold':
                    document.execCommand('bold', false, null);
                    break;
                case 'italic':
                    document.execCommand('italic', false, null);
                    break;
                case 'underline':
                    document.execCommand('underline', false, null);
                    break;
                case 'strikethrough':
                    document.execCommand('strikethrough', false, null);
                    break;
                case 'link':
                    this.showLinkPopup();
                    return;
                case 'image':
                    this.showImagePopup();
                    return;
                case 'blockquote':
                    this.insertBlockquote();
                    break;
                case 'codeblock':
                    this.insertCodeBlock();
                    return;
                case 'inlinecode':
                    this.insertInlineCode();
                    break;
            }

            this.saveSelection();
        }

        toggleSource() {
            if (this.isSourceMode) {
                this.setContent(this.sourceArea.value);
                this.editableArea.style.display = 'block';
                this.sourceArea.style.display = 'none';
                this.isSourceMode = false;
            } else {
                this.sourceArea.value = this.getContent();
                this.editableArea.style.display = 'none';
                this.sourceArea.style.display = 'block';
                this.isSourceMode = true;
            }
        }

        formatHeading(tag) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const parent = range.commonAncestorContainer.parentElement;

            if (parent.tagName && parent.tagName.match(/^H[1-6]$/)) {
                const p = document.createElement('p');
                p.innerHTML = parent.innerHTML;
                parent.replaceWith(p);
            } else {
                document.execCommand('formatBlock', false, tag);
            }
        }

        showLinkPopup(existingLink = null) {
            this.closePopup();
            this.saveSelection();

            const popup = document.createElement('div');
            popup.className = 'miku-popup';
            popup.innerHTML = `
                <div class="miku-popup-header">
                    <span>${existingLink ? 'Edit Link' : 'Insert Link'}</span>
                    <button class="miku-popup-close">&times;</button>
                </div>
                <div class="miku-popup-body">
                    <div class="miku-popup-field">
                        <label>Link Text:</label>
                        <input type="text" id="link-text" value="${existingLink ? existingLink.textContent : ''}" />
                    </div>
                    <div class="miku-popup-field">
                        <label>URL:</label>
                        <input type="text" id="link-url" value="${existingLink ? existingLink.href : 'https://'}" />
                    </div>
                    <div class="miku-popup-field">
                        <label>
                            <input type="checkbox" id="link-target" ${existingLink && existingLink.target === '_blank' ? 'checked' : ''} />
                            Open in new tab
                        </label>
                    </div>
                </div>
                <div class="miku-popup-footer">
                    <button class="miku-btn-primary" id="link-insert">${existingLink ? 'Update' : 'Insert'}</button>
                    <button class="miku-btn-secondary" id="link-cancel">Cancel</button>
                </div>
            `;

            document.body.appendChild(popup);
            this.currentPopup = popup;

            const rect = this.wrapper.getBoundingClientRect();
            popup.style.top = `${rect.top + 100}px`;
            popup.style.left = `${rect.left + (rect.width / 2) - 200}px`;

            popup.querySelector('.miku-popup-close').onclick = () => this.closePopup();
            popup.querySelector('#link-cancel').onclick = () => this.closePopup();
            popup.querySelector('#link-insert').onclick = () => {
                const text = popup.querySelector('#link-text').value;
                const url = popup.querySelector('#link-url').value;
                const target = popup.querySelector('#link-target').checked ? '_blank' : '_self';

                if (existingLink) {
                    existingLink.textContent = text;
                    existingLink.href = url;
                    existingLink.target = target;
                } else {
                    this.insertLink(text, url, target);
                }

                this.closePopup();
            };

            popup.querySelector('#link-text').focus();
        }

        insertLink(text, url, target) {
            if (!text || !url) return;

            const link = document.createElement('a');
            link.href = url;
            link.target = target;
            link.textContent = text;
            link.className = 'miku-editable-link';

            this.restoreSelection();
            const selection = window.getSelection();
            if (selection.rangeCount === 0) return;

            const range = selection.getRangeAt(0);
            range.deleteContents();
            range.insertNode(link);

            range.setStartAfter(link);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
        }

        handleLinkClick(e) {
            if (e.target.tagName === 'A' && e.target.classList.contains('miku-editable-link')) {
                e.preventDefault();

                const editIcon = document.createElement('span');
                editIcon.className = 'miku-link-edit';
                editIcon.innerHTML = '✎';
                editIcon.onclick = (event) => {
                    event.stopPropagation();
                    this.showLinkPopup(e.target);
                    editIcon.remove();
                };

                e.target.parentNode.insertBefore(editIcon, e.target.nextSibling);

                setTimeout(() => editIcon.remove(), 3000);
            }
        }

        handleLinkEditing() {
            document.querySelectorAll('.miku-link-edit').forEach(icon => icon.remove());
        }

        handleKeyDown(e) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const node = range.startContainer;
            const parent = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;

            if (parent.closest('pre[contenteditable="true"]')) {
                if (e.key === 'Tab') {
                    e.preventDefault();
                    document.execCommand('insertText', false, '    ');
                }
                return;
            }

            if (e.key === 'Enter') {
                const code = parent.closest('code');
                if (code && !code.closest('pre')) {
                    e.preventDefault();
                    const textNode = document.createTextNode('\u00A0');
                    code.parentNode.insertBefore(textNode, code.nextSibling);
                    const br = document.createElement('br');
                    textNode.parentNode.insertBefore(br, textNode.nextSibling);
                    const newRange = document.createRange();
                    newRange.setStartAfter(br);
                    newRange.collapse(true);
                    selection.removeAllRanges();
                    selection.addRange(newRange);
                    return;
                }

                const blockquote = parent.closest('blockquote');
                if (blockquote && !e.shiftKey) {
                    e.preventDefault();
                    const p = document.createElement('p');
                    p.innerHTML = '<br>';
                    blockquote.insertAdjacentElement('afterend', p);
                    const newRange = document.createRange();
                    newRange.setStart(p, 0);
                    newRange.collapse(true);
                    selection.removeAllRanges();
                    selection.addRange(newRange);
                }
            }

            if (e.key === 'ArrowRight') {
                const code = parent.closest('code');
                if (code && !code.closest('pre')) {
                    const isAtEnd = range.endOffset === node.length;
                    if (isAtEnd) {
                        e.preventDefault();
                        const textNode = document.createTextNode('\u00A0');
                        if (code.nextSibling) {
                            code.parentNode.insertBefore(textNode, code.nextSibling);
                        } else {
                            code.parentNode.appendChild(textNode);
                        }
                        const newRange = document.createRange();
                        newRange.setStart(textNode, 1);
                        newRange.collapse(true);
                        selection.removeAllRanges();
                        selection.addRange(newRange);
                    }
                }
            }

            if (e.key === 'ArrowLeft') {
                const code = parent.closest('code');
                if (code && !code.closest('pre')) {
                    const isAtStart = range.startOffset === 0;
                    if (isAtStart) {
                        e.preventDefault();
                        const textNode = document.createTextNode('\u00A0');
                        code.parentNode.insertBefore(textNode, code);
                        const newRange = document.createRange();
                        newRange.setStart(textNode, 0);
                        newRange.collapse(true);
                        selection.removeAllRanges();
                        selection.addRange(newRange);
                    }
                }
            }

            if (e.key === 'Backspace') {
                if (range.collapsed && range.startOffset === 0) {
                    const prevSibling = parent.previousElementSibling;
                    if (prevSibling && prevSibling.classList.contains('miku-code-wrapper')) {
                        e.preventDefault();
                        prevSibling.remove();
                    }
                }
            }

            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                setTimeout(() => {
                    const sel = window.getSelection();
                    if (sel.rangeCount > 0) {
                        const r = sel.getRangeAt(0);
                        const n = r.startContainer;
                        const p = n.nodeType === Node.TEXT_NODE ? n.parentElement : n;
                        const code = p.closest('code');
                        if (code && !code.closest('pre')) {
                            const textNode = document.createTextNode('\u00A0');
                            if (e.key === 'ArrowDown') {
                                if (code.nextSibling) {
                                    code.parentNode.insertBefore(textNode, code.nextSibling);
                                } else {
                                    code.parentNode.appendChild(textNode);
                                }
                            } else {
                                code.parentNode.insertBefore(textNode, code);
                            }
                            const newRange = document.createRange();
                            newRange.setStart(textNode, 0);
                            newRange.collapse(true);
                            sel.removeAllRanges();
                            sel.addRange(newRange);
                        }
                    }
                }, 0);
            }
        }

        showImagePopup() {
            this.closePopup();
            this.saveSelection();

            const popup = document.createElement('div');
            popup.className = 'miku-popup';
            popup.innerHTML = `
                <div class="miku-popup-header">
                    <span>Insert Image</span>
                    <button class="miku-popup-close">&times;</button>
                </div>
                <div class="miku-popup-body">
                    <div class="miku-popup-field">
                        <label>Image URL:</label>
                        <input type="text" id="image-url" value="https://" />
                    </div>
                    <div class="miku-popup-field">
                        <label>Display:</label>
                        <select id="image-display">
                            <option value="inline">Inline</option>
                            <option value="block">Block</option>
                        </select>
                    </div>
                </div>
                <div class="miku-popup-footer">
                    <button class="miku-btn-primary" id="image-insert">Insert</button>
                    <button class="miku-btn-secondary" id="image-cancel">Cancel</button>
                </div>
            `;

            document.body.appendChild(popup);
            this.currentPopup = popup;

            const rect = this.wrapper.getBoundingClientRect();
            popup.style.top = `${rect.top + 100}px`;
            popup.style.left = `${rect.left + (rect.width / 2) - 200}px`;

            popup.querySelector('.miku-popup-close').onclick = () => this.closePopup();
            popup.querySelector('#image-cancel').onclick = () => this.closePopup();
            popup.querySelector('#image-insert').onclick = () => {
                const url = popup.querySelector('#image-url').value;
                const display = popup.querySelector('#image-display').value;

                if (url && url !== 'https://') {
                    const link = document.createElement('a');
                    link.href = url;
                    link.target = '_blank';

                    const img = document.createElement('img');
                    img.src = url;
                    img.alt = 'Image';
                    if (display === 'block') img.className = 'block';

                    link.appendChild(img);

                    this.restoreSelection();
                    const selection = window.getSelection();
                    if (selection.rangeCount > 0) {
                        const range = selection.getRangeAt(0);
                        range.deleteContents();
                        range.insertNode(link);
                        range.setStartAfter(link);
                        range.collapse(true);
                        selection.removeAllRanges();
                        selection.addRange(range);
                    } else {
                        this.editableArea.appendChild(link);
                    }

                    this.closePopup();
                }
            };

            popup.querySelector('#image-url').focus();
        }

        insertBlockquote() {
            const selection = window.getSelection();
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const parent = range.commonAncestorContainer.parentElement;

            if (parent.closest('blockquote')) {
                const blockquote = parent.closest('blockquote');
                const p = document.createElement('p');
                p.innerHTML = blockquote.innerHTML;
                blockquote.replaceWith(p);
            } else {
                document.execCommand('formatBlock', false, 'blockquote');
            }
        }

        insertCodeBlock() {
            this.closePopup();

            const codeWrapper = document.createElement('div');
            codeWrapper.className = 'miku-code-wrapper';
            codeWrapper.contentEditable = 'false';

            const langSelect = document.createElement('select');
            langSelect.className = 'miku-code-lang';
            langSelect.innerHTML = LANGUAGES.map(lang =>
                `<option value="${lang}">${lang}</option>`
            ).join('');

            const pre = document.createElement('pre');
            pre.setAttribute('data-language', 'python');
            pre.contentEditable = 'true';
            pre.textContent = '// Your code here...';

            langSelect.onchange = () => {
                pre.setAttribute('data-language', langSelect.value);
            };

            codeWrapper.appendChild(langSelect);
            codeWrapper.appendChild(pre);

            this.restoreSelection();
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                range.deleteContents();
                range.insertNode(codeWrapper);

                const p = document.createElement('p');
                p.innerHTML = '<br>';
                codeWrapper.insertAdjacentElement('afterend', p);

                setTimeout(() => {
                    pre.focus();
                    const newRange = document.createRange();
                    newRange.selectNodeContents(pre);
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(newRange);
                }, 50);
            } else {
                this.editableArea.appendChild(codeWrapper);
                const p = document.createElement('p');
                p.innerHTML = '<br>';
                this.editableArea.appendChild(p);

                setTimeout(() => pre.focus(), 50);
            }
        }

        insertInlineCode() {
            const selection = window.getSelection();
            const selectedText = selection.toString();

            if (selectedText) {
                const code = document.createElement('code');
                code.textContent = selectedText;

                const range = selection.getRangeAt(0);
                range.deleteContents();
                range.insertNode(code);
            } else {
                const code = document.createElement('code');
                code.textContent = 'code';
                this.insertNodeAtCursor(code);
            }
        }

        insertNodeAtCursor(node) {
            const selection = window.getSelection();
            if (!selection.rangeCount) {
                this.editableArea.appendChild(node);
                return;
            }

            const range = selection.getRangeAt(0);
            range.deleteContents();
            range.insertNode(node);

            range.setStartAfter(node);
            range.setEndAfter(node);
            selection.removeAllRanges();
            selection.addRange(range);
        }

        ensureParagraphStructure() {
            const children = Array.from(this.editableArea.childNodes);
            children.forEach(child => {
                if (child.nodeType === Node.TEXT_NODE && child.textContent.trim() !== '') {
                    const p = document.createElement('p');
                    p.textContent = child.textContent;
                    child.replaceWith(p);
                }
            });

            if (this.editableArea.children.length === 0) {
                const p = document.createElement('p');
                p.innerHTML = '<br>';
                this.editableArea.appendChild(p);
            }
        }

        handlePaste(e) {
            e.preventDefault();

            const text = e.clipboardData.getData('text/plain');
            const selection = window.getSelection();

            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            range.deleteContents();

            const lines = text.split('\n');
            lines.forEach((line, index) => {
                const p = document.createElement('p');
                p.textContent = line || '\u00A0';
                range.insertNode(p);

                if (index < lines.length - 1) {
                    range.setStartAfter(p);
                    range.setEndAfter(p);
                }
            });
        }

        closePopup() {
            if (this.currentPopup) {
                this.currentPopup.remove();
                this.currentPopup = null;
            }
        }

        getContent() {
            if (this.isSourceMode) {
                return this.sourceArea.value;
            }

            const clone = this.editableArea.cloneNode(true);
            clone.querySelectorAll('.miku-code-wrapper').forEach(wrapper => {
                const pre = wrapper.querySelector('pre');
                const cleanPre = pre.cloneNode(true);
                cleanPre.removeAttribute('contenteditable');
                wrapper.replaceWith(cleanPre);
            });

            clone.querySelectorAll('.miku-link-edit').forEach(el => el.remove());

            return clone.innerHTML;
        }

        setContent(html) {
            if (this.isSourceMode) {
                this.sourceArea.value = html;
            } else {
                this.editableArea.innerHTML = html || '<p><br></p>';

                this.editableArea.querySelectorAll('pre[data-language]').forEach(pre => {
                    if (!pre.parentElement.classList.contains('miku-code-wrapper')) {
                        const wrapper = document.createElement('div');
                        wrapper.className = 'miku-code-wrapper';
                        wrapper.contentEditable = 'false';

                        const langSelect = document.createElement('select');
                        langSelect.className = 'miku-code-lang';
                        langSelect.innerHTML = LANGUAGES.map(lang =>
                            `<option value="${lang}" ${lang === pre.getAttribute('data-language') ? 'selected' : ''}>${lang}</option>`
                        ).join('');

                        langSelect.onchange = () => {
                            pre.setAttribute('data-language', langSelect.value);
                        };

                        pre.contentEditable = 'true';
                        pre.parentNode.insertBefore(wrapper, pre);
                        wrapper.appendChild(langSelect);
                        wrapper.appendChild(pre);
                    }
                });
            }
        }

        clear() {
            this.editableArea.innerHTML = '<p><br></p>';
            this.sourceArea.value = '';
        }

        destroy() {
            this.closePopup();
            this.container.innerHTML = '';
        }
    }

    window.FancyMiku = FancyMiku;
})();
