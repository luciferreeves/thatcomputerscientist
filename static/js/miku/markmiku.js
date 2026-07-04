(function () {
    'use strict';

    class MarkMikuHighlighter {
        constructor() {}

        escapeHtml(text) {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        wrapSpan(text, className) {
            return '<span class="' + className + '">' + text + '</span>';
        }

        highlight(code) {
            if (!code) return '';

            var result = this.escapeHtml(code);
            var i = 0;
            var out = '';

            while (i < result.length) {
                // Fenced code blocks: ```lang\n...\n```
                if (result.substr(i, 3) === '```') {
                    var lineEnd = result.indexOf('\n', i);
                    if (lineEnd === -1) lineEnd = result.length;
                    var firstLine = result.substring(i, lineEnd);
                    var blockEnd = result.indexOf('\n```', lineEnd);
                    if (blockEnd !== -1) {
                        var lang = firstLine.substring(3);
                        out += this.wrapSpan('```', 'miku-syntax-html-tag');
                        if (lang) out += this.wrapSpan(lang, 'miku-syntax-html-attribute');
                        out += '\n';
                        var content = result.substring(lineEnd + 1, blockEnd);
                        if (content) out += this.wrapSpan(content, 'miku-syntax-html-string');
                        out += '\n' + this.wrapSpan('```', 'miku-syntax-html-tag');
                        i = blockEnd + 4;
                        continue;
                    }
                }

                // Spoiler: ||text||
                if (result.substr(i, 2) === '||') {
                    var spoilerEnd = result.indexOf('||', i + 2);
                    if (spoilerEnd !== -1) {
                        out += this.wrapSpan(result.substring(i, spoilerEnd + 2), 'markmiku-syntax-spoiler');
                        i = spoilerEnd + 2;
                        continue;
                    }
                }

                // Bold: **text**
                if (result.substr(i, 2) === '**') {
                    var boldEnd = result.indexOf('**', i + 2);
                    if (boldEnd !== -1) {
                        out += this.wrapSpan(result.substring(i, boldEnd + 2), 'miku-syntax-js-keyword');
                        i = boldEnd + 2;
                        continue;
                    }
                }

                // Underline: __text__
                if (result.substr(i, 2) === '__') {
                    var underlineEnd = result.indexOf('__', i + 2);
                    if (underlineEnd !== -1) {
                        out += this.wrapSpan(result.substring(i, underlineEnd + 2), 'miku-syntax-js-function');
                        i = underlineEnd + 2;
                        continue;
                    }
                }

                // Strikethrough: ~~text~~
                if (result.substr(i, 2) === '~~') {
                    var strikeEnd = result.indexOf('~~', i + 2);
                    if (strikeEnd !== -1) {
                        out += this.wrapSpan(result.substring(i, strikeEnd + 2), 'miku-syntax-html-comment');
                        i = strikeEnd + 2;
                        continue;
                    }
                }

                // Inline code: `text`
                if (result[i] === '`' && result.substr(i, 3) !== '```') {
                    var codeEnd = result.indexOf('`', i + 1);
                    if (codeEnd !== -1 && result.indexOf('\n', i + 1) > codeEnd) {
                        out += this.wrapSpan(result.substring(i, codeEnd + 1), 'miku-syntax-html-string');
                        i = codeEnd + 1;
                        continue;
                    }
                    if (codeEnd !== -1 && result.indexOf('\n', i + 1) === -1) {
                        out += this.wrapSpan(result.substring(i, codeEnd + 1), 'miku-syntax-html-string');
                        i = codeEnd + 1;
                        continue;
                    }
                }

                // Italic: *text* (single, not preceded by *)
                if (result[i] === '*' && (i === 0 || result[i - 1] !== '*') &&
                    (i + 1 < result.length && result[i + 1] !== '*')) {
                    var italicEnd = result.indexOf('*', i + 1);
                    if (italicEnd !== -1 && result[italicEnd + 1] !== '*') {
                        out += this.wrapSpan(result.substring(i, italicEnd + 1), 'markmiku-syntax-italic');
                        i = italicEnd + 1;
                        continue;
                    }
                }

                // Emoji: :name:
                if (result[i] === ':') {
                    var emojiMatch = result.substring(i).match(/^:([a-z0-9_]+):/);
                    if (emojiMatch) {
                        out += this.wrapSpan(emojiMatch[0], 'markmiku-syntax-emoji');
                        i += emojiMatch[0].length;
                        continue;
                    }
                }

                // Link: [text](url)
                if (result[i] === '[') {
                    var linkMatch = result.substring(i).match(/^\[([^\]]+)\]\(([^)]+)\)/);
                    if (linkMatch) {
                        out += this.wrapSpan('[', 'miku-syntax-html-tag');
                        out += linkMatch[1];
                        out += this.wrapSpan(']', 'miku-syntax-html-tag');
                        out += this.wrapSpan('(', 'miku-syntax-html-tag');
                        out += this.wrapSpan(linkMatch[2], 'miku-syntax-css-value');
                        out += this.wrapSpan(')', 'miku-syntax-html-tag');
                        i += linkMatch[0].length;
                        continue;
                    }
                }

                // Line-start tokens
                if (i === 0 || result[i - 1] === '\n') {
                    // Headings: # ## ###
                    var headingMatch = result.substring(i).match(/^(#{1,3}) /);
                    if (headingMatch) {
                        out += this.wrapSpan(headingMatch[1], 'miku-syntax-css-selector');
                        out += ' ';
                        i += headingMatch[0].length;
                        continue;
                    }

                    // Blockquote: >
                    if (result.substr(i, 2) === '&gt;' || result.substr(i, 5) === '&gt; ') {
                        var gtLen = result.substr(i, 5) === '&gt; ' ? 5 : 4;
                        out += this.wrapSpan(result.substring(i, i + gtLen), 'miku-syntax-html-attribute');
                        i += gtLen;
                        continue;
                    }

                    // List items: - or *
                    if ((result[i] === '-' || result[i] === '*') && result[i + 1] === ' ') {
                        out += this.wrapSpan(result[i], 'miku-syntax-css-property');
                        i++;
                        continue;
                    }

                    // Ordered list: 1. 2. etc.
                    var olMatch = result.substring(i).match(/^(\d+)\. /);
                    if (olMatch) {
                        out += this.wrapSpan(olMatch[1] + '.', 'miku-syntax-css-property');
                        out += ' ';
                        i += olMatch[0].length;
                        continue;
                    }
                }

                out += result[i];
                i++;
            }

            return out;
        }
    }

    class MarkMikuEmojiPicker {
        constructor(editor) {
            this.editor = editor;
            this.emojis = [];
            this.pickerEl = null;
            this.visible = false;
        }

        setEmojis(emojiData) {
            this.emojis = emojiData || [];
        }

        createPicker() {
            if (this.pickerEl) return;

            this.pickerEl = document.createElement('div');
            this.pickerEl.className = 'markmiku-emoji-picker';
            this.pickerEl.style.display = 'none';

            var searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'markmiku-emoji-search';
            searchInput.placeholder = 'Search emojis...';
            searchInput.addEventListener('input', function () {
                this.filterEmojis(searchInput.value);
            }.bind(this));

            var grid = document.createElement('div');
            grid.className = 'markmiku-emoji-grid';

            this.pickerEl.appendChild(searchInput);
            this.pickerEl.appendChild(grid);
            this.gridEl = grid;

            document.body.appendChild(this.pickerEl);
            this.renderGrid(this.emojis);

            document.addEventListener('click', function (e) {
                if (this.visible && !this.pickerEl.contains(e.target) &&
                    !e.target.closest('.markmiku-btn-emoji')) {
                    this.hide();
                }
            }.bind(this));
        }

        renderGrid(emojis) {
            this.gridEl.innerHTML = '';
            for (var i = 0; i < emojis.length; i++) {
                var emoji = emojis[i];
                var item = document.createElement('div');
                item.className = 'markmiku-emoji-item';
                item.title = ':' + emoji.name + ':';
                item.innerHTML = '<img src="' + emoji.url + '" alt=":' + emoji.name + ':" />';
                item.addEventListener('click', (function (em) {
                    return function () {
                        this.insertEmoji(em);
                        this.hide();
                    }.bind(this);
                }.bind(this))(emoji));
                this.gridEl.appendChild(item);
            }
            if (emojis.length === 0) {
                this.gridEl.innerHTML = '<div class="markmiku-emoji-empty">No emojis found</div>';
            }
        }

        filterEmojis(query) {
            if (!query) {
                this.renderGrid(this.emojis);
                return;
            }
            var q = query.toLowerCase();
            var filtered = this.emojis.filter(function (e) {
                return e.name.indexOf(q) !== -1;
            });
            this.renderGrid(filtered);
        }

        show(anchor) {
            this.createPicker();
            this.pickerEl.style.display = 'block';
            this.visible = true;

            if (anchor) {
                var rect = anchor.getBoundingClientRect();
                var pickerHeight = 300;
                var spaceAbove = rect.top;

                this.pickerEl.style.position = 'fixed';
                this.pickerEl.style.left = rect.left + 'px';

                if (spaceAbove > pickerHeight) {
                    this.pickerEl.style.bottom = (window.innerHeight - rect.top + 6) + 'px';
                    this.pickerEl.style.top = 'auto';
                } else {
                    this.pickerEl.style.top = (rect.bottom + 6) + 'px';
                    this.pickerEl.style.bottom = 'auto';
                }
            }

            var search = this.pickerEl.querySelector('.markmiku-emoji-search');
            if (search) {
                search.value = '';
                this.renderGrid(this.emojis);
                search.focus();
            }
        }

        hide() {
            if (this.pickerEl) {
                this.pickerEl.style.display = 'none';
            }
            this.visible = false;
        }

        toggle(anchor) {
            if (this.visible) {
                this.hide();
            } else {
                this.show(anchor);
            }
        }

        insertEmoji(emoji) {
            var textarea = this.editor.editorEl;
            var cursorPos = textarea.selectionStart;
            var before = textarea.value.substring(0, cursorPos);
            var after = textarea.value.substring(textarea.selectionEnd);
            var insert = ':' + emoji.name + ':';

            textarea.value = before + insert + after;
            var newPos = cursorPos + insert.length;
            textarea.setSelectionRange(newPos, newPos);
            textarea.focus();
            this.editor.updateSyntaxHighlighting();
        }

        getAutocomplete(query) {
            if (!query) return [];
            var q = query.toLowerCase();
            return this.emojis.filter(function (e) {
                return e.name.indexOf(q) !== -1;
            }).slice(0, 8);
        }
    }

    class MarkMiku {
        constructor(selector, options) {
            options = options || {};

            if (typeof selector === 'string') {
                this.container = document.querySelector(selector);
            } else {
                this.container = selector;
            }

            if (!this.container) {
                throw new Error('MarkMiku: Element not found');
            }

            this.options = {
                placeholder: options.placeholder || 'Write a message...',
                onSend: options.onSend || null,
                emojis: options.emojis || [],
                attachmentUploadUrl: options.attachmentUploadUrl || null,
                attachmentRemoveUrl: options.attachmentRemoveUrl || null,
                csrfToken: options.csrfToken || '',
                maxAttachments: options.maxAttachments || 8,
                maxAttachmentSize: options.maxAttachmentSize || 33554432
            };

            this.highlighter = new MarkMikuHighlighter();
            this.emojiPicker = new MarkMikuEmojiPicker(this);
            this.emojiPicker.setEmojis(this.options.emojis);

            this.autocompleteVisible = false;
            this.autocompleteItems = [];
            this.autocompleteIndex = -1;
            this.autocompletePrefix = '';

            this.attachments = [];
            this.uploading = 0;

            this.init();
        }

        init() {
            this.createEditor();
            this.bindEvents();
            this.updateSyntaxHighlighting();
        }

        createEditor() {
            this.container.innerHTML = '';
            this.container.className = 'miku-editor-container markmiku-container';

            // Horizontal split: editor column | attachment sidebar
            var body = document.createElement('div');
            body.className = 'markmiku-body';

            var editorCol = document.createElement('div');
            editorCol.className = 'markmiku-editor-col';

            var wrapper = document.createElement('div');
            wrapper.className = 'miku-editor-wrapper';

            var main = document.createElement('div');
            main.className = 'miku-editor-main';

            this.syntaxHighlight = document.createElement('div');
            this.syntaxHighlight.className = 'miku-editor-syntax-highlight';

            this.editorEl = document.createElement('textarea');
            this.editorEl.className = 'miku-editor-input markmiku-input';
            this.editorEl.placeholder = this.options.placeholder;
            this.editorEl.spellcheck = false;
            this.editorEl.rows = 1;

            main.appendChild(this.syntaxHighlight);
            main.appendChild(this.editorEl);
            wrapper.appendChild(main);
            editorCol.appendChild(wrapper);

            // Toolbar
            var toolbar = document.createElement('div');
            toolbar.className = 'markmiku-toolbar';

            // Hidden file input
            this.fileInput = document.createElement('input');
            this.fileInput.type = 'file';
            this.fileInput.multiple = true;
            this.fileInput.style.display = 'none';
            this.container.appendChild(this.fileInput);

            var attachBtn = document.createElement('button');
            attachBtn.type = 'button';
            attachBtn.className = 'markmiku-btn markmiku-btn-attach';
            attachBtn.disabled = !this.options.attachmentUploadUrl;
            attachBtn.title = 'Attach file';
            attachBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>';

            var emojiBtn = document.createElement('button');
            emojiBtn.type = 'button';
            emojiBtn.className = 'markmiku-btn markmiku-btn-emoji';
            emojiBtn.title = 'Emoji';
            emojiBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>';

            var spacer = document.createElement('div');
            spacer.className = 'markmiku-toolbar-spacer';

            var sendBtn = document.createElement('button');
            sendBtn.type = 'button';
            sendBtn.className = 'markmiku-btn markmiku-btn-send';
            sendBtn.title = 'Send';
            sendBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>';

            toolbar.appendChild(attachBtn);
            toolbar.appendChild(emojiBtn);
            toolbar.appendChild(spacer);
            toolbar.appendChild(sendBtn);
            editorCol.appendChild(toolbar);

            // Attachment sidebar
            this.attachmentSidebar = document.createElement('div');
            this.attachmentSidebar.className = 'markmiku-attach-sidebar';
            this.attachmentSidebar.style.display = 'none';

            body.appendChild(editorCol);
            body.appendChild(this.attachmentSidebar);
            this.container.appendChild(body);

            // Autocomplete dropdown
            this.dropdown = document.createElement('div');
            this.dropdown.className = 'miku-editor-autocomplete-dropdown markmiku-autocomplete';
            this.dropdown.style.display = 'none';
            document.body.appendChild(this.dropdown);

            this.sendBtn = sendBtn;
            this.emojiBtn = emojiBtn;
            this.attachBtn = attachBtn;
        }

        bindEvents() {
            var self = this;

            this.editorEl.addEventListener('input', function () {
                self.autoResize();
                self.updateSyntaxHighlighting();
                self.handleEmojiAutocomplete();
            });

            this.editorEl.addEventListener('keydown', function (e) {
                self.handleKeyDown(e);
            });

            this.editorEl.addEventListener('scroll', function () {
                self.syntaxHighlight.scrollTop = self.editorEl.scrollTop;
                self.syntaxHighlight.scrollLeft = self.editorEl.scrollLeft;
            });

            this.sendBtn.addEventListener('click', function () {
                self.send();
            });

            this.emojiBtn.addEventListener('click', function () {
                self.emojiPicker.toggle(self.emojiBtn);
            });

            this.attachBtn.addEventListener('click', function () {
                self.fileInput.click();
            });

            this.fileInput.addEventListener('change', function () {
                var files = Array.prototype.slice.call(self.fileInput.files);
                self.fileInput.value = '';
                for (var i = 0; i < files.length; i++) {
                    self.uploadFile(files[i]);
                }
            });

            document.addEventListener('click', function (e) {
                if (!self.dropdown.contains(e.target) && e.target !== self.editorEl) {
                    self.hideAutocomplete();
                }
            });
        }

        autoResize() {
            this.editorEl.style.height = 'auto';
            var scrollH = this.editorEl.scrollHeight;
            var maxH = 150;
            this.editorEl.style.height = Math.min(scrollH, maxH) + 'px';
            this.syntaxHighlight.style.height = this.editorEl.style.height;
        }

        updateSyntaxHighlighting() {
            var code = this.editorEl.value;
            this.syntaxHighlight.innerHTML = this.highlighter.highlight(code);
            this.syntaxHighlight.scrollTop = this.editorEl.scrollTop;
            this.syntaxHighlight.scrollLeft = this.editorEl.scrollLeft;
        }

        handleEmojiAutocomplete() {
            var cursorPos = this.editorEl.selectionStart;
            var text = this.editorEl.value.substring(0, cursorPos);

            // Look for :query pattern (emoji autocomplete trigger)
            var colonMatch = text.match(/:([a-z0-9_]*)$/);
            if (colonMatch && colonMatch[1].length > 0) {
                var query = colonMatch[1];
                var matches = this.emojiPicker.getAutocomplete(query);
                if (matches.length > 0) {
                    this.autocompletePrefix = colonMatch[0];
                    this.showEmojiAutocomplete(matches, cursorPos);
                    return;
                }
            }
            this.hideAutocomplete();
        }

        showEmojiAutocomplete(emojis, cursorPos) {
            this.autocompleteItems = emojis;
            this.autocompleteIndex = 0;
            this.autocompleteVisible = true;

            this.dropdown.innerHTML = '';
            for (var i = 0; i < emojis.length; i++) {
                var emoji = emojis[i];
                var item = document.createElement('div');
                item.className = 'miku-editor-autocomplete-item';
                item.innerHTML = '<img class="markmiku-autocomplete-emoji-preview" src="' + emoji.url + '" alt="" />' +
                    '<span class="suggestion-text">:' + emoji.name + ':</span>';
                item.addEventListener('click', (function (em) {
                    return function () {
                        this.insertEmojiAutocomplete(em);
                    }.bind(this);
                }.bind(this))(emoji));
                this.dropdown.appendChild(item);
            }

            this.positionDropdown(cursorPos);
            this.dropdown.style.display = 'block';
            this.updateAutocompleteSelection();
        }

        positionDropdown(cursorPos) {
            var coords = this.getCursorCoordinates(cursorPos);
            var dropdownHeight = 200;
            var spaceAbove = coords.y;

            this.dropdown.style.position = 'fixed';
            this.dropdown.style.left = coords.x + 'px';

            if (spaceAbove > dropdownHeight) {
                this.dropdown.style.bottom = (window.innerHeight - coords.y + 5) + 'px';
                this.dropdown.style.top = 'auto';
            } else {
                this.dropdown.style.top = (coords.y + 20) + 'px';
                this.dropdown.style.bottom = 'auto';
            }
        }

        getCursorCoordinates(cursorPos) {
            var editorRect = this.editorEl.getBoundingClientRect();
            var editorStyles = window.getComputedStyle(this.editorEl);

            var tempElement = document.createElement('div');
            tempElement.style.position = 'absolute';
            tempElement.style.visibility = 'hidden';
            tempElement.style.whiteSpace = 'pre-wrap';
            tempElement.style.wordWrap = 'break-word';
            tempElement.style.font = editorStyles.font;
            tempElement.style.fontSize = editorStyles.fontSize;
            tempElement.style.fontFamily = editorStyles.fontFamily;
            tempElement.style.lineHeight = editorStyles.lineHeight;
            tempElement.style.padding = editorStyles.padding;
            tempElement.style.border = editorStyles.border;
            tempElement.style.width = this.editorEl.offsetWidth + 'px';
            tempElement.style.height = 'auto';
            tempElement.style.overflow = 'hidden';

            var textBefore = this.editorEl.value.substring(0, cursorPos);
            var beforeSpan = document.createElement('span');
            beforeSpan.textContent = textBefore;

            var cursorSpan = document.createElement('span');
            cursorSpan.textContent = '|';

            tempElement.appendChild(beforeSpan);
            tempElement.appendChild(cursorSpan);
            document.body.appendChild(tempElement);

            var cursorRect = cursorSpan.getBoundingClientRect();
            var tempRect = tempElement.getBoundingClientRect();
            document.body.removeChild(tempElement);

            return {
                x: editorRect.left + (cursorRect.left - tempRect.left) - this.editorEl.scrollLeft,
                y: editorRect.top + (cursorRect.top - tempRect.top) - this.editorEl.scrollTop
            };
        }

        updateAutocompleteSelection() {
            var items = this.dropdown.querySelectorAll('.miku-editor-autocomplete-item');
            for (var i = 0; i < items.length; i++) {
                if (i === this.autocompleteIndex) {
                    items[i].classList.add('selected');
                } else {
                    items[i].classList.remove('selected');
                }
            }
            if (items[this.autocompleteIndex]) {
                items[this.autocompleteIndex].scrollIntoView({ block: 'nearest' });
            }
        }

        insertEmojiAutocomplete(emoji) {
            var cursorPos = this.editorEl.selectionStart;
            var before = this.editorEl.value.substring(0, cursorPos);
            var after = this.editorEl.value.substring(cursorPos);

            var prefixStart = cursorPos - this.autocompletePrefix.length;
            var insert = ':' + emoji.name + ':';
            this.editorEl.value = before.substring(0, prefixStart) + insert + after;

            var newPos = prefixStart + insert.length;
            this.editorEl.setSelectionRange(newPos, newPos);
            this.editorEl.focus();
            this.hideAutocomplete();
            this.updateSyntaxHighlighting();
        }

        hideAutocomplete() {
            this.dropdown.style.display = 'none';
            this.autocompleteVisible = false;
            this.autocompleteIndex = -1;
            this.autocompleteItems = [];
        }

        handleKeyDown(e) {
            // Autocomplete navigation
            if (this.autocompleteVisible) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.autocompleteIndex = Math.min(this.autocompleteIndex + 1, this.autocompleteItems.length - 1);
                    this.updateAutocompleteSelection();
                    return;
                }
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.autocompleteIndex = Math.max(this.autocompleteIndex - 1, 0);
                    this.updateAutocompleteSelection();
                    return;
                }
                if (e.key === 'Tab' || e.key === 'Enter') {
                    e.preventDefault();
                    if (this.autocompleteIndex >= 0 && this.autocompleteItems[this.autocompleteIndex]) {
                        this.insertEmojiAutocomplete(this.autocompleteItems[this.autocompleteIndex]);
                    }
                    return;
                }
                if (e.key === 'Escape') {
                    this.hideAutocomplete();
                    return;
                }
            }

            // Enter to send (no modifier)
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.send();
                return;
            }

            // Shift+Enter: default newline behavior (no preventDefault)
        }

        uploadFile(file) {
            var self = this;

            if (this.attachments.length >= this.options.maxAttachments) return;
            if (file.size > this.options.maxAttachmentSize) return;

            var tempId = 'tmp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
            var entry = { tempId: tempId, name: file.name, size: file.size, progress: 0, id: null, url: null, xhr: null };
            this.attachments.push(entry);
            this.uploading++;
            this.renderAttachments();

            var formData = new FormData();
            formData.append('file', file);

            var xhr = new XMLHttpRequest();
            entry.xhr = xhr;

            xhr.upload.addEventListener('progress', function (e) {
                if (e.lengthComputable) {
                    entry.progress = Math.round((e.loaded / e.total) * 100);
                    self.renderAttachments();
                }
            });

            xhr.addEventListener('load', function () {
                self.uploading--;
                if (xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    entry.id = data.id;
                    entry.url = data.url;
                    entry.progress = 100;
                } else {
                    self.attachments = self.attachments.filter(function (a) { return a.tempId !== tempId; });
                }
                self.renderAttachments();
            });

            xhr.addEventListener('error', function () {
                self.uploading--;
                self.attachments = self.attachments.filter(function (a) { return a.tempId !== tempId; });
                self.renderAttachments();
            });

            xhr.open('POST', this.options.attachmentUploadUrl);
            xhr.setRequestHeader('X-CSRFToken', this.options.csrfToken);
            xhr.send(formData);
        }

        removeAttachment(tempId) {
            var self = this;
            var entry = this.attachments.find(function (a) { return a.tempId === tempId; });
            if (!entry) return;
            if (entry.progress < 100) return;

            if (entry.id && this.options.attachmentRemoveUrl) {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', this.options.attachmentRemoveUrl.replace('0', entry.id));
                xhr.setRequestHeader('X-CSRFToken', this.options.csrfToken);
                xhr.send();
            }

            this.attachments = this.attachments.filter(function (a) { return a.tempId !== tempId; });
            this.renderAttachments();
        }

        renderAttachments() {
            var self = this;
            var sidebar = this.attachmentSidebar;
            sidebar.innerHTML = '';

            this.attachBtn.disabled = !this.options.attachmentUploadUrl ||
                this.attachments.length >= this.options.maxAttachments;

            if (this.attachments.length === 0) {
                sidebar.style.display = 'none';
                return;
            }

            sidebar.style.display = 'flex';

            for (var i = 0; i < this.attachments.length; i++) {
                var a = this.attachments[i];
                var item = document.createElement('div');
                item.className = 'markmiku-attach-thumb';
                if (a.progress < 100) item.className += ' uploading';

                var isImage = /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(a.name);
                var inner = '';

                if (isImage && a.url) {
                    inner = '<img src="' + a.url + '" alt="" title="' + this.escapeHtml(a.name) + '" />';
                } else {
                    var ext = a.name.split('.').pop().toUpperCase();
                    if (ext.length > 4) ext = ext.substring(0, 4);
                    inner = '<span class="markmiku-attach-ext" title="' + this.escapeHtml(a.name) + '">' + ext + '</span>';
                }

                if (a.progress < 100) {
                    inner += '<div class="markmiku-attach-progress-track"><div class="markmiku-attach-progress-fill" style="height:' + a.progress + '%"></div></div>';
                }

                if (a.progress >= 100) {
                    inner += '<button type="button" class="markmiku-attach-remove" data-id="' + a.tempId + '">&times;</button>';
                }
                item.innerHTML = inner;
                sidebar.appendChild(item);
            }

            var removeBtns = sidebar.querySelectorAll('.markmiku-attach-remove');
            for (var j = 0; j < removeBtns.length; j++) {
                removeBtns[j].addEventListener('click', function () {
                    self.removeAttachment(this.getAttribute('data-id'));
                });
            }
        }

        getAttachmentIds() {
            return this.attachments
                .filter(function (a) { return a.id; })
                .map(function (a) { return a.id; });
        }

        send() {
            var raw = this.editorEl.value.trim();
            if (!raw && this.attachments.length === 0) return;
            if (this.uploading > 0) return;

            var html = raw ? this.markdownToHtml(raw) : '';
            if (this.options.onSend) {
                this.options.onSend(html, this.getAttachmentIds());
            }
            this.editorEl.value = '';
            this.attachments = [];
            this.renderAttachments();
            this.autoResize();
            this.updateSyntaxHighlighting();
        }

        // --- Markdown to HTML converter ---

        markdownToHtml(text) {
            var lines = text.split('\n');
            var html = '';
            var i = 0;
            var inCodeBlock = false;
            var codeLang = '';
            var codeContent = [];
            var listStack = []; // track list type: 'ul' or 'ol'

            while (i < lines.length) {
                var line = lines[i];

                // Fenced code blocks
                if (line.match(/^```/)) {
                    if (!inCodeBlock) {
                        html += this.closeListStack(listStack);
                        inCodeBlock = true;
                        codeLang = line.substring(3).trim();
                        codeContent = [];
                        i++;
                        continue;
                    } else {
                        var langAttr = codeLang ? ' class="language-' + this.escapeAttr(codeLang) + '"' : '';
                        html += '<pre><code' + langAttr + '>' + this.escapeHtml(codeContent.join('\n')) + '</code></pre>';
                        inCodeBlock = false;
                        codeLang = '';
                        codeContent = [];
                        i++;
                        continue;
                    }
                }

                if (inCodeBlock) {
                    codeContent.push(line);
                    i++;
                    continue;
                }

                // Blank line
                if (line.trim() === '') {
                    html += this.closeListStack(listStack);
                    i++;
                    continue;
                }

                // Headings
                var headingMatch = line.match(/^(#{1,3}) (.+)/);
                if (headingMatch) {
                    html += this.closeListStack(listStack);
                    var level = headingMatch[1].length;
                    html += '<h' + level + '>' + this.inlineMarkdown(headingMatch[2]) + '</h' + level + '>';
                    i++;
                    continue;
                }

                // Blockquote
                if (line.match(/^> /)) {
                    html += this.closeListStack(listStack);
                    var quoteLines = [];
                    while (i < lines.length && lines[i].match(/^> /)) {
                        quoteLines.push(lines[i].substring(2));
                        i++;
                    }
                    html += '<blockquote>' + this.inlineMarkdown(quoteLines.join('<br>')) + '</blockquote>';
                    continue;
                }

                // Unordered list
                var ulMatch = line.match(/^[\-\*] (.+)/);
                if (ulMatch) {
                    if (listStack.length === 0 || listStack[listStack.length - 1] !== 'ul') {
                        html += this.closeListStack(listStack);
                        html += '<ul>';
                        listStack.push('ul');
                    }
                    html += '<li>' + this.inlineMarkdown(ulMatch[1]) + '</li>';
                    i++;
                    continue;
                }

                // Ordered list
                var olMatch = line.match(/^\d+\. (.+)/);
                if (olMatch) {
                    if (listStack.length === 0 || listStack[listStack.length - 1] !== 'ol') {
                        html += this.closeListStack(listStack);
                        html += '<ol>';
                        listStack.push('ol');
                    }
                    html += '<li>' + this.inlineMarkdown(olMatch[1]) + '</li>';
                    i++;
                    continue;
                }

                // Regular paragraph
                html += this.closeListStack(listStack);
                html += '<p>' + this.inlineMarkdown(line) + '</p>';
                i++;
            }

            // Close any remaining open code block
            if (inCodeBlock) {
                var langAttr2 = codeLang ? ' class="language-' + this.escapeAttr(codeLang) + '"' : '';
                html += '<pre><code' + langAttr2 + '>' + this.escapeHtml(codeContent.join('\n')) + '</code></pre>';
            }

            html += this.closeListStack(listStack);
            return html;
        }

        closeListStack(stack) {
            var html = '';
            while (stack.length > 0) {
                var tag = stack.pop();
                html += '</' + tag + '>';
            }
            return html;
        }

        inlineMarkdown(text) {
            // Inline code first (protect from other replacements)
            var codeSegments = [];
            text = text.replace(/`([^`]+)`/g, function (m, p1) {
                var idx = codeSegments.length;
                codeSegments.push('<code>' + p1 + '</code>');
                return '\x00CODE' + idx + '\x00';
            });

            // Spoiler: ||text||
            text = text.replace(/\|\|(.+?)\|\|/g, '<span class="markmiku-spoiler">$1</span>');

            // Bold: **text**
            text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            // Underline: __text__
            text = text.replace(/__(.+?)__/g, '<u>$1</u>');

            // Strikethrough: ~~text~~
            text = text.replace(/~~(.+?)~~/g, '<s>$1</s>');

            // Italic: *text* (after bold so ** is consumed first)
            text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

            // Links: [text](url)
            text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

            // Emoji: :name:
            var self = this;
            text = text.replace(/:([a-z0-9_]+):/g, function (match, name) {
                var emoji = self.findEmoji(name);
                if (emoji) {
                    return '<img class="markmiku-emoji" src="' + emoji.url + '" alt=":' + name + ':" title=":' + name + ':" />';
                }
                return match;
            });

            // Restore code segments
            text = text.replace(/\x00CODE(\d+)\x00/g, function (m, idx) {
                return codeSegments[parseInt(idx)];
            });

            return text;
        }

        findEmoji(name) {
            for (var i = 0; i < this.options.emojis.length; i++) {
                if (this.options.emojis[i].name === name) {
                    return this.options.emojis[i];
                }
            }
            return null;
        }

        escapeHtml(text) {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        escapeAttr(text) {
            return text.replace(/[&<>"']/g, function (c) {
                return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
            });
        }

        getContent() {
            return this.editorEl.value;
        }

        getHtml() {
            return this.markdownToHtml(this.editorEl.value);
        }

        clear() {
            this.editorEl.value = '';
            this.autoResize();
            this.updateSyntaxHighlighting();
        }

        focus() {
            this.editorEl.focus();
        }
    }

    window.MarkMiku = MarkMiku;
})();
