#!/usr/bin/env python3
"""
Syntax Highlighter

A simple application to display code with syntax highlighting for multiple languages.
"""

import argparse
import os
import sys
import tempfile
import webbrowser
from pathlib import Path
from typing import Optional, TextIO, Union

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, PythonLexer
from pygments.formatters import TerminalFormatter, HtmlFormatter
from pygments.util import ClassNotFound
from rich.console import Console
from rich.syntax import Syntax


def highlight_code_rich(code: str, language: str, output_file: Optional[TextIO] = None) -> None:
    """
    Highlight code using Rich library and display it in the terminal
    or write to a file if specified.
    
    Args:
        code: The code to highlight
        language: The programming language
        output_file: Optional file to write the highlighted code to
    """
    console = Console(file=output_file or sys.stdout)
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def detect_language(filename: str) -> str:
    """
    Detect the programming language based on the file extension.
    
    Args:
        filename: The name of the file
    
    Returns:
        str: The detected language or 'python' as fallback
    """
    try:
        lexer = get_lexer_for_filename(filename)
        return lexer.aliases[0]
    except ClassNotFound:
        # Default to Python if language can't be detected
        return "python"


def generate_modern_html(code: str, filename: str, language: str) -> str:
    """
    Generate modern HTML with a shadcn-like dark theme for syntax highlighting using Prism.js.
    
    Args:
        code: The code to highlight
        filename: The name of the file being highlighted
        language: The programming language
    
    Returns:
        str: The complete HTML content
    """
    # Create the complete HTML with modern styling and Prism.js
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename} - Syntax Highlighter</title>
    <!-- Prism CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <style>
        /* Modern shadcn-like dark theme */
        :root {{
            --background: #09090b;
            --foreground: #fafafa;
            --card: #171717;
            --card-foreground: #fafafa;
            --popover: #171717;
            --popover-foreground: #fafafa;
            --primary: #6366f1;
            --primary-foreground: #fafafa;
            --secondary: #27272a;
            --secondary-foreground: #fafafa;
            --muted: #27272a;
            --muted-foreground: #a1a1aa;
            --accent: #27272a;
            --accent-foreground: #fafafa;
            --destructive: #ef4444;
            --destructive-foreground: #fafafa;
            --border: #27272a;
            --input: #27272a;
            --ring: #6366f1;
            --radius: 0.5rem;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: var(--background);
            color: var(--foreground);
            line-height: 1.6;
            padding: 0;
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            width: 100%;
        }}

        header {{
            background-color: var(--card);
            border-bottom: 1px solid var(--border);
            padding: 1rem 0;
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--foreground);
            margin: 0;
        }}

        .file-info {{
            font-size: 0.875rem;
            color: var(--muted-foreground);
        }}

        main {{
            flex: 1;
            padding: 2rem 0;
        }}

        .code-container {{
            background-color: var(--card);
            border-radius: var(--radius);
            overflow: hidden;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            position: relative;
        }}

        .code-header {{
            background-color: var(--secondary);
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .code-title {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.875rem;
            color: var(--foreground);
        }}

        .code-actions {{
            display: flex;
            gap: 0.5rem;
        }}

        .code-language {{
            font-size: 0.75rem;
            color: var(--primary);
            background-color: var(--muted);
            padding: 0.25rem 0.5rem;
            border-radius: var(--radius);
        }}

        .button {{
            background-color: var(--muted);
            color: var(--muted-foreground);
            border: none;
            border-radius: var(--radius);
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}

        .button:hover {{
            background-color: var(--primary);
            color: var(--primary-foreground);
        }}

        .button.success {{
            background-color: #10b981;
            color: white;
        }}

        .code-content {{
            padding: 1rem;
            overflow-x: auto;
        }}

        /* Prism.js customizations */
        pre[class*="language-"] {{
            margin: 0;
            border-radius: 0;
            background-color: var(--card);
        }}

        code[class*="language-"] {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.875rem;
            line-height: 1.7;
        }}

        .line-numbers .line-numbers-rows {{
            border-right: 1px solid var(--border);
            opacity: 0.5;
        }}

        .line-numbers-rows > span:before {{
            color: #666 !important;
            opacity: 0.6;
        }}

        footer {{
            background-color: var(--card);
            border-top: 1px solid var(--border);
            padding: 1rem 0;
            font-size: 0.875rem;
            color: var(--muted-foreground);
            text-align: center;
        }}

        /* Language selector */
        .language-selector {{
            position: relative;
            display: inline-block;
        }}

        .language-selector select {{
            appearance: none;
            background-color: var(--muted);
            color: var(--primary);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.25rem 0.5rem;
            padding-right: 1.5rem;
            font-size: 0.75rem;
            cursor: pointer;
        }}

        .language-selector::after {{
            content: '▼';
            font-size: 0.5rem;
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: var(--primary);
        }}

        /* Editor modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            background-color: var(--card);
            border-radius: var(--radius);
            width: 80%;
            max-width: 800px;
            max-height: 90vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}

        .modal-header {{
            background-color: var(--secondary);
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .modal-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--foreground);
        }}

        .modal-close {{
            background: none;
            border: none;
            color: var(--muted-foreground);
            cursor: pointer;
            font-size: 1.5rem;
            line-height: 1;
        }}

        .modal-body {{
            padding: 1rem;
            overflow-y: auto;
            flex: 1;
        }}

        .modal-footer {{
            padding: 1rem;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
        }}

        .code-editor {{
            width: 100%;
            height: 300px;
            background-color: var(--background);
            color: var(--foreground);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.75rem;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.875rem;
            line-height: 1.7;
            resize: vertical;
        }}

        .code-editor:focus {{
            outline: 2px solid var(--ring);
            outline-offset: 2px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <h1>Syntax Highlighter</h1>
            <div class="file-info">
                <span>{filename}</span>
            </div>
        </div>
    </header>
    
    <main class="container">
        <div class="code-container">
            <div class="code-header">
                <span class="code-title">{filename}</span>
                <div class="code-actions">
                    <div class="language-selector">
                        <select id="language-select" onchange="changeLanguage()">
                            <option value="bash">Bash</option>
                            <option value="c">C</option>
                            <option value="cpp">C++</option>
                            <option value="csharp">C#</option>
                            <option value="css">CSS</option>
                            <option value="go">Go</option>
                            <option value="html">HTML</option>
                            <option value="java">Java</option>
                            <option value="javascript">JavaScript</option>
                            <option value="json">JSON</option>
                            <option value="kotlin">Kotlin</option>
                            <option value="markdown">Markdown</option>
                            <option value="php">PHP</option>
                            <option value="python" selected>Python</option>
                            <option value="ruby">Ruby</option>
                            <option value="rust">Rust</option>
                            <option value="sql">SQL</option>
                            <option value="swift">Swift</option>
                            <option value="typescript">TypeScript</option>
                            <option value="yaml">YAML</option>
                        </select>
                    </div>
                    <button class="button" onclick="copyCode()">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        <span>Copy</span>
                    </button>
                    <button class="button" onclick="openEditor()">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                        <span>Edit</span>
                    </button>
                </div>
            </div>
            <div class="code-content">
                <pre><code id="code-display" class="line-numbers language-{language}">{code}</code></pre>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            Generated with Syntax Highlighter
        </div>
    </footer>

    <!-- Editor Modal -->
    <div id="editor-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Edit Code</h2>
                <button class="modal-close" onclick="closeEditor()">&times;</button>
            </div>
            <div class="modal-body">
                <textarea id="code-editor" class="code-editor" spellcheck="false"></textarea>
            </div>
            <div class="modal-footer">
                <button class="button" onclick="closeEditor()">Cancel</button>
                <button class="button success" onclick="updateCode()">Update</button>
            </div>
        </div>
    </div>

    <!-- Prism.js Core -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
    
    <script>
        // Store the original code
        let currentCode = `{code.replace('`', '\\`')}`;
        
        // Set the initial language
        document.addEventListener('DOMContentLoaded', function() {{
            const languageSelect = document.getElementById('language-select');
            languageSelect.value = '{language}';
            
            // Highlight the code
            Prism.highlightAll();
        }});
        
        // Function to copy code to clipboard
        function copyCode() {{
            const copyButton = document.querySelector('.button');
            const copyText = copyButton.querySelector('span');
            
            // Create a temporary textarea to copy the text
            const textarea = document.createElement('textarea');
            textarea.value = currentCode;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            // Update button state
            copyButton.classList.add('success');
            copyText.textContent = 'Copied!';
            
            // Reset button state after 2 seconds
            setTimeout(() => {{
                copyButton.classList.remove('success');
                copyText.textContent = 'Copy';
            }}, 2000);
        }}
        
        // Function to change the language
        function changeLanguage() {{
            const languageSelect = document.getElementById('language-select');
            const codeElement = document.getElementById('code-display');
            const selectedLanguage = languageSelect.value;
            
            // Update the class
            codeElement.className = `line-numbers language-${{selectedLanguage}}`;
            
            // Re-highlight the code
            Prism.highlightElement(codeElement);
        }}
        
        // Function to open the editor modal
        function openEditor() {{
            const modal = document.getElementById('editor-modal');
            const editor = document.getElementById('code-editor');
            
            // Set the current code in the editor
            editor.value = currentCode;
            
            // Show the modal
            modal.classList.add('active');
            
            // Focus the editor
            editor.focus();
        }}
        
        // Function to close the editor modal
        function closeEditor() {{
            const modal = document.getElementById('editor-modal');
            modal.classList.remove('active');
        }}
        
        // Function to update the code from the editor
        function updateCode() {{
            const editor = document.getElementById('code-editor');
            const codeElement = document.getElementById('code-display');
            
            // Update the current code
            currentCode = editor.value;
            
            // Update the displayed code
            codeElement.textContent = currentCode;
            
            // Re-highlight the code
            Prism.highlightElement(codeElement);
            
            // Close the modal
            closeEditor();
        }}
    </script>
</body>
</html>
"""
    return html_content


def highlight_code_html(code: str, output_file: TextIO, language: str) -> None:
    """
    Highlight code and output as HTML.
    
    Args:
        code: The code to highlight
        output_file: File to write the HTML output to
        language: The programming language
    """
    # Get the filename from the command line arguments
    filename = sys.argv[1]
    
    # Generate the modern HTML content
    html_content = generate_modern_html(code, os.path.basename(filename), language)
    
    # Write to the output file
    output_file.write(html_content)


def open_in_browser(code: str, language: str) -> None:
    """
    Generate HTML with syntax highlighting and open it in the default web browser.
    
    Args:
        code: The code to highlight
        language: The programming language
    """
    # Get the filename from the command line arguments
    filename = sys.argv[1]
    
    # Generate the modern HTML content
    html_content = generate_modern_html(code, os.path.basename(filename), language)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_file:
        temp_path = temp_file.name
        temp_file.write(html_content.encode('utf-8'))
    
    # Convert to file:// URL format
    file_url = f"file://{os.path.abspath(temp_path)}"
    
    # Open in browser
    webbrowser.open(file_url)
    print(f"Opened highlighted code in browser: {file_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Highlight code syntax for various languages")
    parser.add_argument("file", help="File to highlight")
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: display in terminal)",
        type=argparse.FileType('w'),
        default=None
    )
    parser.add_argument(
        "--html",
        help="Output as HTML instead of terminal colors",
        action="store_true"
    )
    parser.add_argument(
        "--browser",
        help="Open the highlighted code in a web browser",
        action="store_true"
    )
    parser.add_argument(
        "--language",
        help="Specify the language for syntax highlighting (default: auto-detect)",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        code = Path(args.file).read_text()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Detect or use specified language
    language = args.language or detect_language(args.file)
    
    if args.browser:
        open_in_browser(code, language)
    elif args.html:
        if not args.output:
            print("HTML output requires an output file. Use -o/--output", file=sys.stderr)
            sys.exit(1)
        highlight_code_html(code, args.output, language)
    else:
        highlight_code_rich(code, language, args.output)


if __name__ == "__main__":
    main()
