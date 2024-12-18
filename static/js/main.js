document.getElementById('analyze').addEventListener('click', async () => {
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value;
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const results = await response.json();
        
        if (response.ok) {
            displayResults(results);
        } else {
            alert(`Error: ${results.error}`);
        }
    } catch (error) {
        alert('Error analyzing page: ' + error);
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    for (const [cls, articles] of Object.entries(results)) {
        const classContainer = document.createElement('div');
        classContainer.className = 'class-container';
        
        const header = document.createElement('div');
        header.className = 'class-header';
        
        const classInfo = document.createElement('div');
        classInfo.className = 'class-info';
        classInfo.innerHTML = `
            <div class="class-name">Class: ${cls}</div>
            <div class="stats">Number of articles: ${articles.length}</div>
        `;
        
        const exportButton = document.createElement('button');
        exportButton.className = 'export-button';
        exportButton.textContent = 'Export to JSON';
        exportButton.onclick = () => exportClass(cls, articles);
        
        header.appendChild(classInfo);
        header.appendChild(exportButton);
        classContainer.appendChild(header);
        
        articles.forEach(article => {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'article';
            articleDiv.textContent = article;
            classContainer.appendChild(articleDiv);
        });
        
        resultsDiv.appendChild(classContainer);
    }
}

function exportClass(className, articles) {
    const jsonData = JSON.stringify({ [className]: articles }, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `class_${className}.json`;
    document.body.appendChild(a);
    a.click();
    
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
} 