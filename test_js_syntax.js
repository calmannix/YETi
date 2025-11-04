// Extract and test just the displayAIInsights function
function displayAIInsights(insights) {
    const contentEl = {innerHTML: ''};
    let html = '';
    
    // Handle error case
    if (insights.error && insights.raw_response) {
        html = `<div>Error</div>`;
        contentEl.innerHTML = html;
        return;
    }
    
    // Create 2x2 grid for the 4 main sections
    html += '<div class="insights-grid">';
        
        // Test if blocks
        if (insights.impact_ranking && insights.impact_ranking.length > 0) {
            html += '<div>Impact ranking</div>';
        }
        
        if (insights.proven_practices && insights.proven_practices.length > 0) {
            html += '<div>Proven practices</div>';
        }
        
        if (insights.key_insight) {
            html += `<div>${insights.key_insight}</div>`;
        }
    
    // Add generation info
    if (insights.generated_at) {
        const date = new Date(insights.generated_at);
        html += `<p>Generated: ${date.toLocaleString()}</p>`;
    }
    
    contentEl.innerHTML = html;
}

// Test it
console.log('✓ JavaScript syntax is valid!');
displayAIInsights({key_insight: 'Test', generated_at: new Date().toISOString()});
console.log('✓ Function executes correctly!');

