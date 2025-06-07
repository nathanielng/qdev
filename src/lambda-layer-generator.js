document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const versionButtons = document.querySelectorAll('.version-btn');
  const pyenvBtn = document.getElementById('pyenvBtn');
  const uvBtn = document.getElementById('uvBtn');
  const librariesTextarea = document.getElementById('libraries');
  const zipNameInput = document.getElementById('zipName');
  const generatedCodeElement = document.getElementById('generatedCode');
  const copyBtn = document.getElementById('copyBtn');
  const downloadBtn = document.getElementById('downloadBtn');

  // State
  let selectedVersion = '3.10';
  let packageManager = 'pyenv';
  
  // Initialize
  generateCode();

  // Event listeners
  versionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      versionButtons.forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedVersion = btn.dataset.version;
      generateCode();
    });
  });

  pyenvBtn.addEventListener('click', () => {
    pyenvBtn.classList.add('selected');
    uvBtn.classList.remove('selected');
    packageManager = 'pyenv';
    generateCode();
  });

  uvBtn.addEventListener('click', () => {
    uvBtn.classList.add('selected');
    pyenvBtn.classList.remove('selected');
    packageManager = 'uv';
    generateCode();
  });

  librariesTextarea.addEventListener('input', generateCode);
  zipNameInput.addEventListener('input', generateCode);

  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(generatedCodeElement.textContent)
      .then(() => {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span>Copied!</span>';
        setTimeout(() => {
          copyBtn.innerHTML = originalText;
        }, 2000);
      });
  });

  downloadBtn.addEventListener('click', () => {
    const filename = `lambda-layer-${packageManager}-py${selectedVersion.replace('.', '')}.sh`;
    const text = generatedCodeElement.textContent;
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  });

  // Generate code based on current selections
  function generateCode() {
    const libraries = librariesTextarea.value.trim();
    const zipName = zipNameInput.value.trim() || 'lambda-layer';
    const pyVersion = selectedVersion;
    const pyShortVersion = pyVersion.replace('.', '');
    
    let code = '';
    
    // Create requirements.txt content
    const requirementsContent = libraries || 'requests==2.32.3';
    
    if (packageManager === 'pyenv') {
      code = `mkdir -p layer-build/ && cd layer-build/
pyenv local ${pyVersion}
pyenv which python

cat << EOF > requirements.txt
${requirementsContent}
EOF

python -m venv create_layer
source create_layer/bin/activate
pip install -r requirements.txt
mkdir -p python
cp -r create_layer/lib python/
zip -r ${zipName}-py${pyShortVersion}.zip python

# Cleanup
deactivate
rm -rf create_layer/ python/
`;
    } else {
      code = `mkdir -p layer-build/ && cd layer-build/
cat << EOF > requirements.txt
${requirementsContent}
EOF

uv venv --python ${pyVersion} create_layer/
source create_layer/bin/activate
uv pip install -r requirements.txt
mkdir -p python
cp -r create_layer/lib python/
zip -r ${zipName}-py${pyShortVersion}.zip python

# Cleanup
deactivate
rm -rf create_layer/ python/
`;
    }
    
    generatedCodeElement.textContent = code;
    Prism.highlightElement(generatedCodeElement);
  }
});
