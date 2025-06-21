(function () {
    'use strict';

    class TinyMikuSyntaxHighlighter {
        constructor() {
        }

        escapeHtml(text) {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        wrapSpan(text, className) {
            return `<span class="${className}">${text}</span>`;
        }

        highlight(code) {
            if (!code) return '';

            let result = this.escapeHtml(code);
            let i = 0;
            let highlightedResult = '';

            while (i < result.length) {
                if (result.substr(i, 3) === '```') {
                    const blockStart = i;
                    let lineEnd = result.indexOf('\n', i);
                    if (lineEnd === -1) lineEnd = result.length;

                    const firstLine = result.substring(i, lineEnd);
                    const langMatch = firstLine.match(/```(lang-\w*)/);

                    const blockEnd = result.indexOf('\n```', lineEnd);
                    if (blockEnd !== -1) {
                        const content = result.substring(lineEnd + 1, blockEnd);

                        highlightedResult += this.wrapSpan('```', 'miku-syntax-html-tag');

                        if (langMatch) {
                            const langAttr = langMatch[1];
                            highlightedResult += this.wrapSpan(langAttr, 'miku-syntax-html-attribute');
                        }

                        highlightedResult += '\n';

                        if (content) {
                            highlightedResult += this.wrapSpan(content, 'miku-syntax-html-string');
                        }

                        highlightedResult += '\n' + this.wrapSpan('```', 'miku-syntax-html-tag');

                        i = blockEnd + 4;
                        continue;
                    }
                }

                if (result.substr(i, 2) === '$$') {
                    const mathStart = i;
                    const mathEnd = result.indexOf('$$', i + 2);
                    if (mathEnd !== -1) {
                        const mathContent = result.substring(mathStart, mathEnd + 2);
                        highlightedResult += this.wrapSpan(mathContent, 'miku-syntax-css-value');
                        i = mathEnd + 2;
                        continue;
                    }
                }

                if (result[i] === '$' && (i === 0 || result[i - 1] !== '$') &&
                    (i + 1 >= result.length || result[i + 1] !== '$')) {
                    const mathStart = i;
                    const mathEnd = result.indexOf('$', i + 1);
                    if (mathEnd !== -1) {
                        const mathContent = result.substring(mathStart, mathEnd + 1);
                        highlightedResult += this.wrapSpan(mathContent, 'miku-syntax-css-property');
                        i = mathEnd + 1;
                        continue;
                    }
                }

                if (result.substr(i, 2) === '**') {
                    const boldStart = i;
                    const boldEnd = result.indexOf('**', i + 2);
                    if (boldEnd !== -1) {
                        const boldContent = result.substring(boldStart, boldEnd + 2);
                        highlightedResult += this.wrapSpan(boldContent, 'miku-syntax-js-keyword');
                        i = boldEnd + 2;
                        continue;
                    }
                }

                if (result.substr(i, 2) === '__') {
                    const italicStart = i;
                    const italicEnd = result.indexOf('__', i + 2);
                    if (italicEnd !== -1) {
                        const italicContent = result.substring(italicStart, italicEnd + 2);
                        highlightedResult += this.wrapSpan(italicContent, 'miku-syntax-js-function');
                        i = italicEnd + 2;
                        continue;
                    }
                }

                if (result.substr(i, 2) === '~~') {
                    const strikeStart = i;
                    const strikeEnd = result.indexOf('~~', i + 2);
                    if (strikeEnd !== -1) {
                        const strikeContent = result.substring(strikeStart, strikeEnd + 2);
                        highlightedResult += this.wrapSpan(strikeContent, 'miku-syntax-html-comment');
                        i = strikeEnd + 2;
                        continue;
                    }
                }

                highlightedResult += result[i];
                i++;
            }

            return highlightedResult;
        }
    }

    class TinyMikuAutocomplete {
        constructor() {
            this.markupTags = [
                { text: '**', type: 'bold', insertText: '****' },
                { text: '__', type: 'italic', insertText: '____' },
                { text: '~~', type: 'strikethrough', insertText: '~~~~' },
                { text: '```', type: 'code-block', insertText: '```lang-\n\n```' },
                { text: '$$', type: 'math-block', insertText: '$$$$' },
                { text: '$', type: 'math-inline', insertText: '$$' }
            ];
        }

        getSuggestions(prefix, context, customWords = []) {
            const suggestions = [];
            const lowerPrefix = prefix.toLowerCase();

            this.markupTags.forEach(tag => {
                if (tag.text.startsWith(prefix)) {
                    suggestions.push(tag);
                }
            });

            if (customWords && customWords.size > 0) {
                customWords.forEach(word => {
                    if (word.toLowerCase().startsWith(lowerPrefix) &&
                        word.toLowerCase() !== lowerPrefix &&
                        !suggestions.some(s => s.text === word)) {
                        suggestions.push({
                            text: word,
                            type: 'custom-word',
                            insertText: word
                        });
                    }
                });
            }

            return suggestions.slice(0, 10);
        }
    }

    class TinyMiku {
        constructor(selector, options = {}) {
            if (typeof selector === 'string') {
                this.container = document.querySelector(selector);
            } else {
                this.container = selector;
            }

            if (!this.container) {
                throw new Error('Tiny Miku Editor: Element not found');
            }

            this.options = {
                placeholder: 'Start typing...',
                ...options
            };

            this.highlighter = new TinyMikuSyntaxHighlighter();
            this.autocomplete = new TinyMikuAutocomplete();

            this.selectedIndex = -1;
            this.suggestions = [];
            this.currentPrefix = '';
            this.customWords = new Set();

            this.init();
        }

        init() {
            this.createEditor();
            this.bindEvents();
            this.updateSyntaxHighlighting();
        }

        createEditor() {
            this.container.className = 'miku-editor-container';
            this.container.innerHTML = `
                <div class="miku-editor-wrapper">
                    <div class="miku-editor-main">
                        <div class="miku-editor-syntax-highlight" id="mikuSyntaxHighlight"></div>
                        <textarea 
                            class="miku-editor-input" 
                            id="mikuEditor" 
                            placeholder="${this.options.placeholder}"
                            spellcheck="false"
                        ></textarea>
                    </div>
                </div>
                <div class="miku-editor-autocomplete-dropdown" id="mikuAutocompleteDropdown"></div>
            `;

            this.editor = this.container.querySelector('#mikuEditor');
            this.syntaxHighlight = this.container.querySelector('#mikuSyntaxHighlight');
            this.dropdown = this.container.querySelector('#mikuAutocompleteDropdown');
        }

        bindEvents() {
            this.editor.addEventListener('input', () => {
                this.updateSyntaxHighlighting();
                this.handleInput();
            });

            this.editor.addEventListener('keydown', (e) => {
                this.handleKeyDown(e);
            });

            this.editor.addEventListener('scroll', () => {
                this.syntaxHighlight.scrollTop = this.editor.scrollTop;
                this.syntaxHighlight.scrollLeft = this.editor.scrollLeft;
                if (this.dropdown.style.display === 'block') {
                    const cursorPos = this.editor.selectionStart;
                    if (cursorPos !== undefined) {
                        this.positionDropdown(cursorPos);
                    }
                }
            });

            this.editor.addEventListener('click', () => {
                if (this.dropdown.style.display === 'block') {
                    const cursorPos = this.editor.selectionStart;
                    if (cursorPos !== undefined) {
                        this.positionDropdown(cursorPos);
                    }
                }
            });

            this.editor.addEventListener('keyup', (e) => {
                if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key)) {
                    if (this.dropdown.style.display === 'block') {
                        const cursorPos = this.editor.selectionStart;
                        if (cursorPos !== undefined) {
                            this.positionDropdown(cursorPos);
                        }
                    }
                }
            });

            document.addEventListener('click', (e) => {
                if (!this.dropdown.contains(e.target) && e.target !== this.editor) {
                    this.hideDropdown();
                }
            });
        }

        updateSyntaxHighlighting() {
            const code = this.editor.value;
            const highlighted = this.highlighter.highlight(code);
            this.syntaxHighlight.innerHTML = highlighted;
            this.syntaxHighlight.scrollTop = this.editor.scrollTop;
            this.syntaxHighlight.scrollLeft = this.editor.scrollLeft;
        }

        handleInput() {
            const cursorPos = this.editor.selectionStart;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const currentWord = this.getCurrentWord(textBeforeCursor);

            this.extractCustomWords();

            if (currentWord.length > 0) {
                this.showAutocomplete(currentWord, cursorPos);
            } else {
                this.hideDropdown();
            }
        }

        extractCustomWords() {
            const content = this.editor.value;
            const wordPattern = /[\w-]{3,}/g;
            const words = content.match(wordPattern) || [];

            words.forEach(word => {
                if (word.length >= 3) {
                    this.customWords.add(word);
                }
            });
        }

        getCurrentWord(text) {
            const match = text.match(/[\w\-\*\_\~\`\$]*$/);
            return match ? match[0] : '';
        }

        showAutocomplete(prefix, cursorPos) {
            this.currentPrefix = prefix;
            this.suggestions = this.autocomplete.getSuggestions(prefix, null, this.customWords);

            if (this.suggestions.length === 0) {
                this.hideDropdown();
                return;
            }

            this.renderDropdown();
            this.positionDropdown(cursorPos);
            this.selectedIndex = 0;
            this.updateSelection();
        }

        renderDropdown() {
            this.dropdown.innerHTML = '';
            this.suggestions.forEach((suggestion, index) => {
                const item = document.createElement('div');
                item.className = 'miku-editor-autocomplete-item';

                if (suggestion.type === 'custom-word') {
                    item.classList.add('custom-word-suggestion');
                }

                item.innerHTML = `
                    <span class="suggestion-text">${suggestion.text}</span>
                    <span class="suggestion-type">${suggestion.type}</span>
                `;
                item.addEventListener('click', () => {
                    this.insertSuggestion(suggestion);
                });
                this.dropdown.appendChild(item);
            });
            this.dropdown.style.display = 'block';
        }

        positionDropdown(cursorPos) {
            const coords = this.getCursorCoordinates(cursorPos);
            const editorRect = this.editor.getBoundingClientRect();
            const viewportHeight = window.innerHeight;

            let leftPos = coords.x;
            const dropdownWidth = 200;
            const dropdownHeight = Math.min(200, this.suggestions.length * 34);

            if (leftPos + dropdownWidth > editorRect.right - 5) {
                leftPos = Math.max(editorRect.right - dropdownWidth - 5, editorRect.left + 5);
            }

            if (leftPos < editorRect.left + 5) {
                leftPos = editorRect.left + 5;
            }

            let topPos = coords.y + 25;

            if (topPos + dropdownHeight > Math.min(editorRect.bottom - 5, viewportHeight - 10)) {
                topPos = coords.y - dropdownHeight - 5;
                if (topPos < 10) {
                    topPos = coords.y + 25;
                }
            }

            this.dropdown.style.left = leftPos + 'px';
            this.dropdown.style.top = topPos + 'px';
        }

        getCursorCoordinates(cursorPos) {
            const editorRect = this.editor.getBoundingClientRect();
            const editorStyles = window.getComputedStyle(this.editor);

            const tempElement = document.createElement('div');
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
            tempElement.style.width = this.editor.offsetWidth + 'px';
            tempElement.style.height = 'auto';
            tempElement.style.overflow = 'hidden';

            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const textAfterCursor = this.editor.value.substring(cursorPos);

            const beforeSpan = document.createElement('span');
            beforeSpan.textContent = textBeforeCursor;

            const cursorSpan = document.createElement('span');
            cursorSpan.textContent = '|';
            cursorSpan.style.color = 'transparent';

            const afterSpan = document.createElement('span');
            afterSpan.textContent = textAfterCursor;

            tempElement.appendChild(beforeSpan);
            tempElement.appendChild(cursorSpan);
            tempElement.appendChild(afterSpan);

            document.body.appendChild(tempElement);

            const cursorRect = cursorSpan.getBoundingClientRect();
            const tempRect = tempElement.getBoundingClientRect();

            document.body.removeChild(tempElement);

            const x = editorRect.left + (cursorRect.left - tempRect.left) - this.editor.scrollLeft;
            const y = editorRect.top + (cursorRect.top - tempRect.top) - this.editor.scrollTop;

            return { x: x, y: y };
        }

        handleKeyDown(e) {
            if (this.dropdown.style.display === 'block') {
                switch (e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1);
                        this.updateSelection();
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                        this.updateSelection();
                        break;
                    case 'Tab':
                    case 'Enter':
                        e.preventDefault();
                        if (this.selectedIndex >= 0) {
                            this.insertSuggestion(this.suggestions[this.selectedIndex]);
                        }
                        break;
                    case 'Escape':
                        this.hideDropdown();
                        break;
                }
                return;
            }

            if (e.key === 'Tab') {
                e.preventDefault();
                this.insertTabSpaces();
                return;
            }

            if (e.key === 'Enter') {
                this.handleAutoIndent(e);
                return;
            }

            this.handleAutoClose(e);
        }

        handleAutoClose(e) {
            const bracketPairs = {
                '(': ')',
                '[': ']',
                '{': '}',
                '<': '>'
            };

            const quotePairs = {
                '"': '"',
                "'": "'"
            };

            const key = e.key;

            if (bracketPairs[key] || quotePairs[key]) {
                e.preventDefault();

                const cursorPos = this.editor.selectionStart;
                const textBeforeCursor = this.editor.value.substring(0, cursorPos);
                const textAfterCursor = this.editor.value.substring(cursorPos);
                const selectedText = this.editor.value.substring(this.editor.selectionStart, this.editor.selectionEnd);

                let closingChar;

                if (bracketPairs[key]) {
                    closingChar = bracketPairs[key];
                } else if (quotePairs[key]) {
                    closingChar = quotePairs[key];

                    if (textAfterCursor.startsWith(closingChar)) {
                        this.insertText(key);
                        return;
                    }
                }

                if (selectedText) {
                    const newText = key + selectedText + closingChar;
                    this.insertText(newText);
                    this.editor.setSelectionRange(cursorPos + 1, cursorPos + 1 + selectedText.length);
                } else {
                    this.insertText(key + closingChar);
                    this.editor.setSelectionRange(cursorPos + 1, cursorPos + 1);
                }
            }
        }

        insertText(text) {
            const cursorPos = this.editor.selectionStart;
            const selectionEnd = this.editor.selectionEnd;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const textAfterCursor = this.editor.value.substring(selectionEnd);

            this.editor.value = textBeforeCursor + text + textAfterCursor;
            this.updateSyntaxHighlighting();
        }

        updateSelection() {
            const items = this.dropdown.querySelectorAll('.miku-editor-autocomplete-item');
            items.forEach((item, index) => {
                item.classList.toggle('selected', index === this.selectedIndex);
            });

            if (items[this.selectedIndex]) {
                items[this.selectedIndex].scrollIntoView({ block: 'nearest' });
            }
        }

        insertSuggestion(suggestion) {
            const cursorPos = this.editor.selectionStart;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const textAfterCursor = this.editor.value.substring(cursorPos);

            const prefixStart = cursorPos - this.currentPrefix.length;
            const newText = textBeforeCursor.substring(0, prefixStart) + suggestion.insertText + textAfterCursor;

            this.editor.value = newText;

            let newCursorPos = prefixStart + suggestion.insertText.length;

            if (suggestion.insertText === '****') {
                newCursorPos = prefixStart + 2;
            } else if (suggestion.insertText === '____') {
                newCursorPos = prefixStart + 2;
            } else if (suggestion.insertText === '~~~~') {
                newCursorPos = prefixStart + 2;
            } else if (suggestion.insertText === '$$') {
                newCursorPos = prefixStart + 2;
            } else if (suggestion.insertText === '$' && suggestion.type === 'math-inline') {
                newCursorPos = prefixStart + 1;
            } else if (suggestion.insertText === '```lang-\n\n```') {
                newCursorPos = prefixStart + 7;
            }

            this.editor.setSelectionRange(newCursorPos, newCursorPos);
            this.editor.focus();
            this.hideDropdown();
            this.updateSyntaxHighlighting();
        }

        insertTabSpaces() {
            const tabSize = 4;
            const cursorPos = this.editor.selectionStart;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const textAfterCursor = this.editor.value.substring(cursorPos);

            const spaces = ' '.repeat(tabSize);
            const newText = textBeforeCursor + spaces + textAfterCursor;

            this.editor.value = newText;
            const newCursorPos = cursorPos + tabSize;
            this.editor.setSelectionRange(newCursorPos, newCursorPos);

            this.updateSyntaxHighlighting();
        }

        handleAutoIndent(e) {
            if (e.key === 'Enter') {
                e.preventDefault();

                const cursorPos = this.editor.selectionStart;
                const textBeforeCursor = this.editor.value.substring(0, cursorPos);
                const textAfterCursor = this.editor.value.substring(cursorPos);

                const currentLineMatch = textBeforeCursor.match(/[^\n]*$/);
                const currentLine = currentLineMatch ? currentLineMatch[0] : '';

                const indentMatch = currentLine.match(/^[ \t]*/);
                const indent = indentMatch ? indentMatch[0] : '';

                this.editor.value = textBeforeCursor + '\n' + indent + textAfterCursor;
                const newCursorPos = cursorPos + 1 + indent.length;
                this.editor.setSelectionRange(newCursorPos, newCursorPos);

                this.updateSyntaxHighlighting();
            }
        }

        hideDropdown() {
            this.dropdown.style.display = 'none';
            this.selectedIndex = -1;
            this.suggestions = [];
        }
    }

    window.TinyMiku = TinyMiku;
})();