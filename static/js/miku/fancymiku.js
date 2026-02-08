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

            const icons = {
                h1: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M2.243 4.493v7.5m0 0v7.502m0-7.501h10.5m0-7.5v7.5m0 0v7.501m4.501-8.627 2.25-1.5v10.126m0 0h-2.25m2.25 0h2.25" /></svg>`,
                h2: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 19.5H16.5v-1.609a2.25 2.25 0 0 1 1.244-2.012l2.89-1.445c.651-.326 1.116-.955 1.116-1.683 0-.498-.04-.987-.118-1.463-.135-.825-.835-1.422-1.668-1.489a15.202 15.202 0 0 0-3.464.12M2.243 4.492v7.5m0 0v7.502m0-7.501h10.5m0-7.5v7.5m0 0v7.501" /></svg>`,
                h3: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M20.905 14.626a4.52 4.52 0 0 1 .738 3.603c-.154.695-.794 1.143-1.504 1.208a15.194 15.194 0 0 1-3.639-.104m4.405-4.707a4.52 4.52 0 0 0 .738-3.603c-.154-.696-.794-1.144-1.504-1.209a15.19 15.19 0 0 0-3.639.104m4.405 4.708H18M2.243 4.493v7.5m0 0v7.502m0-7.501h10.5m0-7.5v7.5m0 0v7.501" /></svg>`,
                bold: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linejoin="round" d="M6.75 3.744h-.753v8.25h7.125a4.125 4.125 0 0 0 0-8.25H6.75Zm0 0v.38m0 16.122h6.747a4.5 4.5 0 0 0 0-9.001h-7.5v9h.753Zm0 0v-.37m0-15.751h6a3.75 3.75 0 1 1 0 7.5h-6m0-7.5v7.5m0 0v8.25m0-8.25h6.375a4.125 4.125 0 0 1 0 8.25H6.75m.747-15.38h4.875a3.375 3.375 0 0 1 0 6.75H7.497v-6.75Zm0 7.5h5.25a3.75 3.75 0 0 1 0 7.5h-5.25v-7.5Z" /></svg>`,
                italic: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M5.248 20.246H9.05m0 0h3.696m-3.696 0 5.893-16.502m0 0h-3.697m3.697 0h3.803" /></svg>`,
                underline: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M17.995 3.744v7.5a6 6 0 1 1-12 0v-7.5m-2.25 16.502h16.5" /></svg>`,
                strikethrough: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 12a8.912 8.912 0 0 1-.318-.079c-1.585-.424-2.904-1.247-3.76-2.236-.873-1.009-1.265-2.19-.968-3.301.59-2.2 3.663-3.29 6.863-2.432A8.186 8.186 0 0 1 16.5 5.21M6.42 17.81c.857.99 2.176 1.812 3.761 2.237 3.2.858 6.274-.23 6.863-2.431.233-.868.044-1.779-.465-2.617M3.75 12h16.5" /></svg>`,
                link: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" /></svg>`,
                image: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" /></svg>`,
                blockquote: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" /></svg>`,
                codeblock: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0 0 21 18V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v12a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>`,
                inlinecode: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5" /></svg>`,
                source: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" /></svg>`
            }

            const buttons = [
                { icon: icons.h1, title: 'Heading 1', command: 'heading', value: 'h1' },
                { icon: icons.h2, title: 'Heading 2', command: 'heading', value: 'h2' },
                { icon: icons.h3, title: 'Heading 3', command: 'heading', value: 'h3' },
                { separator: true },
                { icon: icons.bold, title: 'Bold', command: 'bold' },
                { icon: icons.italic, title: 'Italic', command: 'italic' },
                { icon: icons.underline, title: 'Underline', command: 'underline' },
                { icon: icons.strikethrough, title: 'Strikethrough', command: 'strikethrough' },
                { separator: true },
                { icon: icons.link, title: 'Insert Link', command: 'link' },
                { icon: icons.image, title: 'Insert Image', command: 'image' },
                { separator: true },
                { icon: icons.blockquote, title: 'Blockquote', command: 'blockquote' },
                { icon: icons.codeblock, title: 'Code Block', command: 'codeblock' },
                { icon: icons.inlinecode, title: 'Inline Code', command: 'inlinecode' },
                { separator: true },
                { icon: icons.source, title: 'Toggle Source', command: 'togglesource', special: true }
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
