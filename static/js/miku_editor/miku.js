(function () {
    `use strict`;
    class MikuSyntaxHighlighter {
        constructor() {
            this.htmlTags = [
                `html`, `head`, `title`, `body`, `div`, `span`, `p`, `a`, `img`, `ul`, `li`, `ol`,
                `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `strong`, `em`, `br`, `hr`, `table`, `tr`,
                `td`, `th`, `thead`, `tbody`, `form`, `input`, `button`, `select`, `option`,
                `textarea`, `label`, `section`, `article`, `header`, `footer`, `nav`, `aside`,
                `main`, `figure`, `figcaption`, `video`, `audio`, `source`, `canvas`, `svg`,
                `style`, `script`, `link`, `meta`
            ];

            this.cssProperties = [
                `background`, `background-color`, `background-image`, `color`, `font-family`,
                `font-size`, `font-weight`, `margin`, `padding`, `border`, `width`, `height`,
                `display`, `position`, `top`, `left`, `right`, `bottom`, `z-index`, `opacity`,
                `text-align`, `text-decoration`, `line-height`, `border-radius`, `box-shadow`
            ];

            this.cssValues = [
                `auto`, `none`, `block`, `inline`, `flex`, `grid`, `absolute`, `relative`,
                `fixed`, `center`, `left`, `right`, `bold`, `normal`, `hidden`, `visible`
            ];

            this.jsKeywords = [
                `function`, `var`, `let`, `const`, `if`, `else`, `for`, `while`, `do`, `switch`,
                `case`, `default`, `break`, `continue`, `return`, `try`, `catch`, `finally`,
                `throw`, `new`, `this`, `class`, `import`, `export`, `async`, `await`
            ];
        }

        escapeHtml(text) {
            return text
                .replace(/&/g, `&amp;`)
                .replace(/</g, `&lt;`)
                .replace(/>/g, `&gt;`)
                .replace(/"/g, `&quot;`)
                .replace(/'/g, `&#39;`);
        }

        wrapSpan(text, className) {
            return `<span class="${className}">${text}</span>`;
        }

        highlightHtmlTag(tag) {
            const escapedTag = this.escapeHtml(tag);
            let result = escapedTag;

            result = result.replace(/&lt;(\/?)([\w-]+)((?:\s+(?:[\w-:]+(?:\s*=\s*(?:&quot;[^&]*&quot;|'[^']*'|[^\s&>]*))?))*)&gt;/g,
                (match, slash, tagName, attributesStr) => {
                    const startBracket = '&lt;' + slash;
                    const endBracket = '&gt;';
                    const highlightedTagName = this.wrapSpan(tagName, 'miku-syntax-html-tag');

                    let processedAttributes = attributesStr;

                    if (attributesStr && attributesStr.trim()) {
                        processedAttributes = attributesStr.replace(/\s+([\w-:]+)(?:\s*=\s*(&quot;[^&]*&quot;|'[^']*'|[^\s&>]*))?/g,
                            (attrMatch, attrName, attrValue) => {
                                let result = ' ' + this.wrapSpan(attrName, 'miku-syntax-html-attribute');

                                if (attrValue !== undefined) {
                                    if (attrValue.startsWith('&quot;') || attrValue.startsWith("'")) {
                                        result += '=' + this.wrapSpan(attrValue, 'miku-syntax-html-string');
                                    } else {
                                        result += '=' + attrValue;
                                    }
                                }

                                return result;
                            }
                        );
                    }

                    return startBracket + highlightedTagName + processedAttributes + endBracket;
                }
            );

            return result;
        }

        highlightCSS(code) {
            if (!code.trim()) return this.escapeHtml(code);

            let result = ``;
            let i = 0;

            while (i < code.length) {
                if (code.substr(i, 2) === `/*`) {
                    const commentEnd = code.indexOf(`*/`, i);
                    if (commentEnd !== -1) {
                        const comment = code.substring(i, commentEnd + 2);
                        result += `<span class="miku-syntax-css-comment">${this.escapeHtml(comment)}</span>`;
                        i = commentEnd + 2;
                        continue;
                    }
                }

                if (/[a-zA-Z-]/.test(code[i])) {
                    let word = ``;
                    let wordStart = i;

                    while (i < code.length && /[a-zA-Z-]/.test(code[i])) {
                        word += code[i];
                        i++;
                    }

                    let nextChar = i;
                    while (nextChar < code.length && /\s/.test(code[nextChar])) {
                        nextChar++;
                    }

                    if (nextChar < code.length && code[nextChar] === `:`) {
                        if (this.cssProperties.includes(word)) {
                            result += `<span class="miku-syntax-css-property">${this.escapeHtml(word)}</span>`;
                        } else {
                            result += this.escapeHtml(word);
                        }
                    } else {
                        if (this.cssValues.includes(word.toLowerCase())) {
                            result += `<span class="miku-syntax-css-value">${this.escapeHtml(word)}</span>`;
                        } else {
                            result += this.escapeHtml(word);
                        }
                    }
                    continue;
                }

                result += this.escapeHtml(code[i]);
                i++;
            }

            return result;
        }

        highlightJS(code) {
            if (!code.trim()) return this.escapeHtml(code);

            let result = ``;
            let i = 0;

            while (i < code.length) {
                if (code.substr(i, 2) === `//`) {
                    const lineEnd = code.indexOf(`\n`, i);
                    const comment = lineEnd !== -1 ? code.substring(i, lineEnd) : code.substring(i);
                    result += `<span class="miku-syntax-js-comment">${this.escapeHtml(comment)}</span>`;
                    i = lineEnd !== -1 ? lineEnd : code.length;
                    continue;
                }

                if (code.substr(i, 2) === `/*`) {
                    const commentEnd = code.indexOf(`*/`, i);
                    if (commentEnd !== -1) {
                        const comment = code.substring(i, commentEnd + 2);
                        result += `<span class="miku-syntax-js-comment">${this.escapeHtml(comment)}</span>`;
                        i = commentEnd + 2;
                        continue;
                    }
                }

                if (code[i] === `"` || code[i] === `'` || code[i] === `\``) {
                    const quote = code[i];
                    let string = quote;
                    i++;

                    while (i < code.length && code[i] !== quote) {
                        if (code[i] === `\\` && i + 1 < code.length) {
                            string += code[i] + code[i + 1];
                            i += 2;
                        } else {
                            string += code[i];
                            i++;
                        }
                    }

                    if (i < code.length) {
                        string += code[i];
                        i++;
                    }

                    result += `<span class="miku-syntax-js-string">${this.escapeHtml(string)}</span>`;
                    continue;
                }

                if (/\d/.test(code[i])) {
                    let number = ``;
                    while (i < code.length && /[\d.]/.test(code[i])) {
                        number += code[i];
                        i++;
                    }
                    result += `<span class="miku-syntax-js-number">${this.escapeHtml(number)}</span>`;
                    continue;
                }

                if (/[a-zA-Z_$]/.test(code[i])) {
                    let word = ``;
                    while (i < code.length && /[a-zA-Z0-9_$]/.test(code[i])) {
                        word += code[i];
                        i++;
                    }

                    if (this.jsKeywords.includes(word)) {
                        result += `<span class="miku-syntax-js-keyword">${this.escapeHtml(word)}</span>`;
                    } else {
                        let nextChar = i;
                        while (nextChar < code.length && /\s/.test(code[nextChar])) {
                            nextChar++;
                        }
                        if (nextChar < code.length && code[nextChar] === `(`) {
                            result += `<span class="miku-syntax-js-function">${this.escapeHtml(word)}</span>`;
                        } else {
                            result += this.escapeHtml(word);
                        }
                    }
                    continue;
                }

                result += this.escapeHtml(code[i]);
                i++;
            }

            return result;
        }

        highlight(code) {
            if (!code) return ``;

            let result = ``;
            let i = 0;

            while (i < code.length) {
                if (code.substr(i, 4) === `<!--`) {
                    const commentEnd = code.indexOf(`-->`, i);
                    if (commentEnd !== -1) {
                        const comment = code.substring(i, commentEnd + 3);
                        result += this.wrapSpan(this.escapeHtml(comment), `miku-syntax-html-comment`);
                        i = commentEnd + 3;
                        continue;
                    }
                }

                if (code.substr(i, 6).toLowerCase() === `<style`) {
                    const styleStart = i;
                    const styleTagEnd = code.indexOf(`>`, i);
                    const styleEnd = code.indexOf(`</style>`, styleTagEnd);

                    if (styleTagEnd !== -1 && styleEnd !== -1) {
                        const openTag = code.substring(styleStart, styleTagEnd + 1);
                        const cssContent = code.substring(styleTagEnd + 1, styleEnd);
                        const closeTag = code.substring(styleEnd, styleEnd + 8);

                        result += this.highlightHtmlTag(openTag);
                        result += this.highlightCSS(cssContent);
                        result += this.highlightHtmlTag(closeTag);

                        i = styleEnd + 8;
                        continue;
                    }
                }

                if (code.substr(i, 7).toLowerCase() === `<script`) {
                    const scriptStart = i;
                    const scriptTagEnd = code.indexOf(`>`, i);
                    const scriptEnd = code.indexOf(`</script>`, scriptTagEnd);

                    if (scriptTagEnd !== -1 && scriptEnd !== -1) {
                        const openTag = code.substring(scriptStart, scriptTagEnd + 1);
                        const jsContent = code.substring(scriptTagEnd + 1, scriptEnd);
                        const closeTag = code.substring(scriptEnd, scriptEnd + 9);

                        result += this.highlightHtmlTag(openTag);
                        result += this.highlightJS(jsContent);
                        result += this.highlightHtmlTag(closeTag);

                        i = scriptEnd + 9;
                        continue;
                    }
                }

                if (code[i] === `<` && i + 1 < code.length && /[a-zA-Z\/!]/.test(code[i + 1])) {
                    let j = i + 1;
                    let inQuotes = false;
                    let quoteChar = null;
                    let tagEnd = -1;

                    while (j < code.length) {
                        if (!inQuotes && code[j] === '>') {
                            tagEnd = j;
                            break;
                        }

                        if ((code[j] === '"' || code[j] === "'") && (j === 0 || code[j - 1] !== '\\')) {
                            if (!inQuotes) {
                                inQuotes = true;
                                quoteChar = code[j];
                            } else if (code[j] === quoteChar) {
                                inQuotes = false;
                            }
                        }
                        j++;
                    }

                    if (tagEnd !== -1) {
                        const tag = code.substring(i, tagEnd + 1);
                        result += this.highlightHtmlTag(tag);
                        i = tagEnd + 1;
                        continue;
                    }
                }

                result += this.escapeHtml(code[i]);
                i++;
            }

            return result;
        }
    }

    class MikuAutocomplete {
        constructor() {
            this.htmlTags = [
                `html`, `head`, `title`, `body`, `div`, `span`, `p`, `a`, `ul`, `li`, `ol`,
                `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `strong`, `em`, `table`, `tr`,
                `td`, `th`, `thead`, `tbody`, `form`, `button`, `select`, `option`,
                `textarea`, `label`, `section`, `article`, `header`, `footer`, `nav`, `aside`,
                `main`, `figure`, `figcaption`, `video`, `audio`, `source`, `canvas`, `svg`,
                `style`, `script`, `link`, `meta`
            ];

            this.voidElements = [
                `br`, `hr`, `img`, `input`, `meta`, `link`, `area`, `base`, `col`,
                `embed`, `source`, `track`, `wbr`
            ];

            this.htmlAttributes = [
                `id`, `class`, `style`, `src`, `href`, `alt`, `title`, `data-`, `role`,
                `type`, `name`, `value`, `placeholder`, `required`, `disabled`, `readonly`,
                `width`, `height`, `target`, `rel`, `for`, `method`, `action`
            ];

            this.cssProperties = [
                `background`, `background-color`, `background-image`, `background-size`,
                `color`, `font-family`, `font-size`, `font-weight`, `font-style`, `text-align`,
                `text-decoration`, `line-height`, `margin`, `margin-top`, `margin-bottom`,
                `margin-left`, `margin-right`, `padding`, `padding-top`, `padding-bottom`,
                `padding-left`, `padding-right`, `border`, `border-radius`, `width`, `height`,
                `display`, `position`, `top`, `bottom`, `left`, `right`, `z-index`, `opacity`
            ];

            this.cssValues = [
                `auto`, `none`, `inherit`, `initial`, `block`, `inline`, `inline-block`, `flex`,
                `grid`, `absolute`, `relative`, `fixed`, `static`, `center`, `left`, `right`,
                `bold`, `normal`, `italic`, `underline`, `hidden`, `visible`
            ];

            this.jsKeywords = [
                `function`, `var`, `let`, `const`, `if`, `else`, `for`, `while`, `do`, `switch`,
                `case`, `default`, `break`, `continue`, `return`, `try`, `catch`, `finally`,
                `throw`, `new`, `this`, `super`, `class`, `extends`, `import`, `export`,
                `from`, `as`, `async`, `await`, `typeof`, `instanceof`, `in`, `of`, `delete`
            ];

            this.jsMethods = [
                `console.log`, `document.getElementById`, `document.querySelector`,
                `addEventListener`, `setTimeout`, `setInterval`, `JSON.parse`, `JSON.stringify`,
                `Math.floor`, `Math.ceil`, `Math.round`, `Math.random`, `fetch`, `alert`
            ];

            this.emmetAbbreviations = {
                div: `<div></div>`,
                p: `<p></p>`,
                span: `<span></span>`,
                a: `<a href=""></a>`,
                ul: `<ul>\n\t<li></li>\n</ul>`,
                ol: `<ol>\n\t<li></li>\n</ol>`,
                button: `<button></button>`,
                style: `<style>\n\t\n</style>`,
                script: `<script>\n\t\n</script>`,
                br: `<br>`,
                hr: `<hr>`,
                img: `<img src="" alt="">`,
                input: `<input type="text">`,
                meta: `<meta name="" content="">`,
                link: `<link rel="stylesheet" href="">`
            };
        }

        getSuggestions(prefix, context, customWords = []) {
            const suggestions = [];
            const lowerPrefix = prefix.toLowerCase();

            switch (context) {
                case `css`:
                    this.cssProperties.forEach(prop => {
                        if (prop.startsWith(lowerPrefix)) {
                            suggestions.push({
                                text: prop,
                                type: `css-property`,
                                insertText: `${prop}: `
                            });
                        }
                    });

                    this.cssValues.forEach(value => {
                        if (value.startsWith(lowerPrefix)) {
                            suggestions.push({
                                text: value,
                                type: `css-value`,
                                insertText: value
                            });
                        }
                    });
                    break;

                case `javascript`:
                    this.jsKeywords.forEach(keyword => {
                        if (keyword.startsWith(lowerPrefix)) {
                            suggestions.push({
                                text: keyword,
                                type: `js-keyword`,
                                insertText: keyword
                            });
                        }
                    });

                    this.jsMethods.forEach(method => {
                        if (method.toLowerCase().startsWith(lowerPrefix)) {
                            suggestions.push({
                                text: method,
                                type: `js-method`,
                                insertText: method
                            });
                        }
                    });
                    break;

                default:
                    this.htmlTags.forEach(tag => {
                        if (tag.startsWith(lowerPrefix)) {
                            const isVoidElement = this.voidElements.includes(tag);
                            const insertText = isVoidElement ? `<${tag}>` : `<${tag}></${tag}>`;

                            suggestions.push({
                                text: tag,
                                type: `html-tag`,
                                insertText: insertText
                            });
                        }
                    });

                    this.htmlAttributes.forEach(attr => {
                        if (attr.startsWith(lowerPrefix)) {
                            suggestions.push({
                                text: attr,
                                type: `html-attribute`,
                                insertText: `${attr}=""`
                            });
                        }
                    });

                    Object.keys(this.emmetAbbreviations).forEach(abbr => {
                        if (abbr.startsWith(lowerPrefix)) {
                            suggestions.push({
                                text: abbr,
                                type: `emmet`,
                                insertText: this.emmetAbbreviations[abbr]
                            });
                        }
                    });
                    break;
            }

            if (customWords && customWords.size > 0) {
                customWords.forEach(word => {
                    if (word.toLowerCase().startsWith(lowerPrefix) &&
                        word.toLowerCase() !== lowerPrefix &&
                        !suggestions.some(s => s.text === word)) {
                        suggestions.push({
                            text: word,
                            type: "custom-word",
                            insertText: word
                        });
                    }
                });
            }

            return suggestions.slice(0, 15);
        }
    }

    class Miku {
        constructor(selector, options = {}) {
            if (typeof selector === `string`) {
                this.container = document.querySelector(selector);
            } else {
                this.container = selector;
            }

            if (!this.container) {
                throw new Error(`Miku Editor: Element not found`);
            }

            this.options = {
                placeholder: `Start Typing...`,
                ...options
            };

            this.highlighter = new MikuSyntaxHighlighter();
            this.autocomplete = new MikuAutocomplete();

            this.selectedIndex = -1;
            this.suggestions = [];
            this.currentPrefix = ``;
            this.currentContext = `html`;
            this.customWords = new Set();

            this.init();
        }

        init() {
            this.createEditor();
            this.bindEvents();
            this.updateLineNumbers();
            this.updateSyntaxHighlighting();
        }

        createEditor() {
            this.container.className = `miku-editor-container`;
            this.container.innerHTML = `
                <div class="miku-editor-wrapper">
                    <div class="miku-editor-line-numbers" id="mikuLineNumbers">1</div>
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

            this.editor = this.container.querySelector(`#mikuEditor`);
            this.lineNumbers = this.container.querySelector(`#mikuLineNumbers`);
            this.syntaxHighlight = this.container.querySelector(`#mikuSyntaxHighlight`);
            this.dropdown = this.container.querySelector(`#mikuAutocompleteDropdown`);
        }

        bindEvents() {
            this.editor.addEventListener(`input`, () => {
                this.updateLineNumbers();
                this.updateSyntaxHighlighting();
                this.handleInput();
            });

            this.editor.addEventListener(`keydown`, (e) => {
                this.handleKeyDown(e);
            });

            this.editor.addEventListener(`scroll`, () => {
                this.lineNumbers.scrollTop = this.editor.scrollTop;
                this.syntaxHighlight.scrollTop = this.editor.scrollTop;
                this.syntaxHighlight.scrollLeft = this.editor.scrollLeft;

                if (this.dropdown.style.display === `block`) {
                    const cursorPos = this.editor.selectionStart;
                    if (cursorPos !== undefined) {
                        this.positionDropdown(cursorPos);
                    }
                }
            });

            this.editor.addEventListener(`click`, () => {
                this.updateContext();
            });

            this.editor.addEventListener(`keyup`, () => {
                this.updateContext();
            });

            document.addEventListener(`click`, (e) => {
                if (!this.dropdown.contains(e.target) && e.target !== this.editor) {
                    this.hideDropdown();
                }
            });
        }

        updateLineNumbers() {
            const lines = this.editor.value.split(`\n`).length;
            const lineNumbersHTML = Array.from({ length: lines }, (_, i) => i + 1).join(`\n`);
            this.lineNumbers.textContent = lineNumbersHTML;
        }

        syncScrolling() {
            this.lineNumbers.scrollTop = this.editor.scrollTop;
            this.syntaxHighlight.scrollTop = this.editor.scrollTop;
            this.syntaxHighlight.scrollLeft = this.editor.scrollLeft;
        }

        updateSyntaxHighlighting() {
            const code = this.editor.value;
            const highlighted = this.highlighter.highlight(code);
            this.syntaxHighlight.innerHTML = highlighted;
            this.syncScrolling();
        }

        updateContext() {
            const cursorPos = this.editor.selectionStart;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);

            const styleStart = textBeforeCursor.lastIndexOf(`<style`);
            const styleEnd = textBeforeCursor.lastIndexOf(`</style>`);

            const scriptStart = textBeforeCursor.lastIndexOf(`<script`);
            const scriptEnd = textBeforeCursor.lastIndexOf(`</script>`);

            const styleAttrMatch = textBeforeCursor.match(/style\s*=\s*"[^"]*$/i);

            if (styleStart > styleEnd && styleStart !== -1) {
                const styleTagEnd = textBeforeCursor.indexOf(`>`, styleStart);
                if (styleTagEnd !== -1 && cursorPos > styleTagEnd) {
                    this.currentContext = `css`;
                } else {
                    this.currentContext = `html`;
                }
            } else if (scriptStart > scriptEnd && scriptStart !== -1) {
                const scriptTagEnd = textBeforeCursor.indexOf(`>`, scriptStart);
                if (scriptTagEnd !== -1 && cursorPos > scriptTagEnd) {
                    this.currentContext = `javascript`;
                } else {
                    this.currentContext = `html`;
                }
            } else if (styleAttrMatch) {
                this.currentContext = `css`;
            } else {
                this.currentContext = `html`;
            }
        }

        handleInput() {
            this.updateContext();
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
            const match = text.match(/[\w-]*$/);
            return match ? match[0] : ``;
        }

        showAutocomplete(prefix, cursorPos) {
            this.currentPrefix = prefix;
            this.suggestions = this.autocomplete.getSuggestions(prefix, this.currentContext, this.customWords);

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
            this.dropdown.innerHTML = ``;
            this.suggestions.forEach((suggestion, index) => {
                const item = document.createElement(`div`);
                item.className = `miku-editor-autocomplete-item`;

                if (suggestion.type === "custom-word") {
                    item.classList.add("custom-word-suggestion");
                }

                item.innerHTML = `
                    <span class="suggestion-text">${suggestion.text}</span>
                    <span class="suggestion-type">${suggestion.type}</span>
                `;
                item.addEventListener(`click`, () => {
                    this.insertSuggestion(suggestion);
                });
                this.dropdown.appendChild(item);
            });
            this.dropdown.style.display = `block`;
        }

        positionDropdown(cursorPos) {
            const coords = this.getCursorCoordinates(cursorPos);
            const editorRect = this.editor.getBoundingClientRect();

            const x = coords.x;
            const y = coords.y;

            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            const dropdownWidth = this.dropdown.offsetWidth || 200;
            const dropdownHeight = Math.min(200, this.suggestions.length * 34);

            let leftPos = x;

            const editorWidth = editorRect.width;
            const editorPadding = 5;

            if (leftPos + dropdownWidth > editorRect.right - editorPadding) {
                leftPos = Math.max(
                    editorRect.right - dropdownWidth - editorPadding,
                    editorRect.left + editorPadding
                );
            }

            if (leftPos < editorRect.left + editorPadding) {
                leftPos = editorRect.left + editorPadding;
            }

            if (leftPos + dropdownWidth > viewportWidth - 10) {
                leftPos = viewportWidth - dropdownWidth - 10;
            }

            let topPos = y + 25;

            if (topPos + dropdownHeight > Math.min(editorRect.bottom - editorPadding, viewportHeight - 10)) {
                topPos = y - dropdownHeight - 5;
            }

            if (topPos < editorRect.top + editorPadding) {
                topPos = editorRect.top + editorPadding;
            }

            this.dropdown.style.left = leftPos + `px`;
            this.dropdown.style.top = topPos + `px`;

            this.dropdown.dataset.visible = 'true';
        }

        getCursorCoordinates(cursorPos) {
            const editorRect = this.editor.getBoundingClientRect();
            const editorStyles = window.getComputedStyle(this.editor);

            const paddingLeft = parseInt(editorStyles.paddingLeft, 10);
            const paddingTop = parseInt(editorStyles.paddingTop, 10);

            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const lines = textBeforeCursor.split(`\n`);

            const lineHeight = parseInt(editorStyles.lineHeight, 10) ||
                parseInt(editorStyles.fontSize, 10) * 1.4;

            const lineNumber = lines.length - 1;
            const lineText = lines[lineNumber];

            const canvas = document.createElement(`canvas`);
            const ctx = canvas.getContext(`2d`);
            ctx.font = `${editorStyles.fontSize} ${editorStyles.fontFamily}`;

            const textWidth = ctx.measureText(lineText).width;
            const scrollLeft = this.editor.scrollLeft;

            const tempSpan = document.createElement('span');
            tempSpan.textContent = 'A';
            tempSpan.style.visibility = 'hidden';
            tempSpan.style.position = 'absolute';
            tempSpan.style.font = `${editorStyles.fontSize} ${editorStyles.fontFamily}`;

            const charWidth = ctx.measureText('A').width;
            let adjustedX = editorRect.left + paddingLeft + textWidth - scrollLeft;

            adjustedX = Math.max(adjustedX, editorRect.left + paddingLeft);
            adjustedX = Math.min(adjustedX, editorRect.right - paddingLeft);

            const y = editorRect.top + paddingTop + (lineNumber * lineHeight);

            return { x: adjustedX, y: y };
        }

        handleKeyDown(e) {
            if (this.dropdown.style.display === `block`) {
                switch (e.key) {
                    case `ArrowDown`:
                        e.preventDefault();
                        this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1);
                        this.updateSelection();
                        break;
                    case `ArrowUp`:
                        e.preventDefault();
                        this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                        this.updateSelection();
                        break;
                    case `Tab`:
                    case `Enter`:
                        e.preventDefault();
                        if (this.selectedIndex >= 0) {
                            this.insertSuggestion(this.suggestions[this.selectedIndex]);
                        }
                        break;
                    case `Escape`:
                        this.hideDropdown();
                        break;
                }
            } else if (e.key === `Tab`) {
                e.preventDefault();
                const emmetExpanded = this.handleEmmetExpansion();

                if (!emmetExpanded) {
                    this.insertTabSpaces();
                }
            } else if (e.key === `Enter`) {
                this.handleAutoIndent(e);
            } else {
                this.handleAutoClose(e);
            }
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
                "'": "'",
                '`': '`'
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

                    if (textAfterCursor.startsWith(closingChar) ||
                        (textBeforeCursor.endsWith(key) && !this.isEscaped(textBeforeCursor, textBeforeCursor.length - 1))) {
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

        isEscaped(text, position) {
            let count = 0;
            let i = position - 1;

            while (i >= 0 && text[i] === '\\') {
                count++;
                i--;
            }

            return count % 2 !== 0;
        }

        insertText(text) {
            const cursorPos = this.editor.selectionStart;
            const selectionEnd = this.editor.selectionEnd;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const textAfterCursor = this.editor.value.substring(selectionEnd);

            this.editor.value = textBeforeCursor + text + textAfterCursor;
            this.updateLineNumbers();
            this.updateSyntaxHighlighting();
        }

        updateSelection() {
            const items = this.dropdown.querySelectorAll(`.miku-editor-autocomplete-item`);
            items.forEach((item, index) => {
                item.classList.toggle(`selected`, index === this.selectedIndex);
            });

            if (items[this.selectedIndex]) {
                items[this.selectedIndex].scrollIntoView({ block: `nearest` });
            }
        }

        insertSuggestion(suggestion) {
            const cursorPos = this.editor.selectionStart;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const textAfterCursor = this.editor.value.substring(cursorPos);

            const prefixStart = cursorPos - this.currentPrefix.length;
            const newText = textBeforeCursor.substring(0, prefixStart) +
                suggestion.insertText + textAfterCursor;

            this.editor.value = newText;

            let newCursorPos = prefixStart + suggestion.insertText.length;
            if (suggestion.insertText.includes(`""`)) {
                newCursorPos = prefixStart + suggestion.insertText.indexOf(`""`) + 1;
            } else if (suggestion.insertText.includes(`></`)) {
                newCursorPos = prefixStart + suggestion.insertText.indexOf(`></`) + 1;
            } else if (suggestion.insertText.includes(`: `)) {
                newCursorPos = prefixStart + suggestion.insertText.length;
            }

            this.editor.setSelectionRange(newCursorPos, newCursorPos);
            this.editor.focus();
            this.hideDropdown();
            this.updateLineNumbers();
            this.updateSyntaxHighlighting();
        }

        handleEmmetExpansion() {
            const cursorPos = this.editor.selectionStart;
            const textBeforeCursor = this.editor.value.substring(0, cursorPos);
            const currentWord = this.getCurrentWord(textBeforeCursor);

            if (this.autocomplete.emmetAbbreviations[currentWord]) {
                const suggestion = {
                    text: currentWord,
                    type: `emmet`,
                    insertText: this.autocomplete.emmetAbbreviations[currentWord]
                };
                this.currentPrefix = currentWord;
                this.insertSuggestion(suggestion);
                return true;
            }
            return false;
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

            this.updateLineNumbers();
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

                let extraIndent = '';
                if (currentLine.trim().endsWith('{') ||
                    currentLine.trim().endsWith('(') ||
                    currentLine.trim().endsWith('[')) {
                    extraIndent = ' '.repeat(4);
                }

                this.editor.value = textBeforeCursor + '\n' + indent + extraIndent + textAfterCursor;

                const newCursorPos = cursorPos + 1 + indent.length + extraIndent.length;
                this.editor.setSelectionRange(newCursorPos, newCursorPos);

                this.updateLineNumbers();
                this.updateSyntaxHighlighting();
                return true;
            }
            return false;
        }

        hideDropdown() {
            this.dropdown.style.display = `none`;
            this.selectedIndex = -1;
            this.suggestions = [];
        }
    }

    window.Miku = Miku;
})();
