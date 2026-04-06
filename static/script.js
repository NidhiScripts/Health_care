document.addEventListener('DOMContentLoaded', () => {
    
    document.getElementById('run-btn').addEventListener('click', async () => {
        const btn = document.getElementById('run-btn');
        const diff = document.getElementById('difficulty').value;
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const container = document.getElementById('steps-container');
        const finalPanel = document.getElementById('final-output');
        
        // Reset state
        btn.disabled = true;
        btn.innerText = "Processing Engine...";
        container.innerHTML = '';
        results.classList.add('hidden');
        finalPanel.classList.remove('animate-in'); // Reset scale anim
        loading.classList.remove('hidden');
        
        try {
            // Fetch dynamically from Flask backend
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ difficulty: diff })
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert("Backend Error: " + data.error);
                return;
            }
            
            // Build elements strictly off screen first
            loading.classList.add('hidden');
            results.classList.remove('hidden');
            
            // Animate trace array sequentially!
            await playSequence(data.steps);
            
            // Render Final Module Scale-up
            document.getElementById('final-diagnosis').innerText = data.final_diagnosis;
            document.getElementById('total-steps').innerText = data.steps.length;
            document.getElementById('total-reward').innerText = data.total_reward.toFixed(1);
            document.getElementById('final-score').innerText = `${data.score.toFixed(1)} / 1.0`;
            
            const scoreBox = document.getElementById('score-box');
            scoreBox.className = 'stat-box'; // reset class
            
            if (data.score > 0) {
                scoreBox.classList.add('success');
            } else {
                scoreBox.classList.add('failure');
            }
            
            // Trigger the scale animation on the final results board
            setTimeout(() => {
                finalPanel.classList.add('animate-in');
            }, 300); // slight buffer after the final step trace completes

        } catch (err) {
            console.error(err);
            alert("A critical error occurred binding the application logic.");
        } finally {
            btn.disabled = false;
            btn.innerText = "Run Diagnosis";
            loading.classList.add('hidden');
        }
    });

    /**
     * Recreates the timeline asynchronously feeding sequential CSS fade triggers
     */
    async function playSequence(steps) {
        const container = document.getElementById('steps-container');
        
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            const stepDiv = document.createElement('div');
            stepDiv.className = 'step-item';
            
            const isDiagnose = step.action_type === 'diagnose';
            const icon = isDiagnose ? '🩺' : '🧪';
            const title = isDiagnose ? `Diagnosis: ${step.value}` : `Test: <span>${step.value}</span>`;
            
            // Injecting the new dynamic contextual reasoning string map directly to the HTML
            stepDiv.innerHTML = `
                <div class="step-icon">${icon}</div>
                <div class="step-content">
                    <div class="step-title">Step ${step.step} &rarr; ${title}</div>
                    <div class="step-reason">Reason: ${step.reason}</div>
                </div>
                <div class="step-badge">Reward: ${step.reward.toFixed(1)}</div>
            `;
            
            container.appendChild(stepDiv);
            
            // Small timeout payload triggering CSS injection frame logic seamlessly
            await new Promise(resolve => setTimeout(() => {
                stepDiv.classList.add('animate-in');
                resolve();
            }, 50));
            
            // Wait slightly between steps mimicking "processing" organically.
            await new Promise(resolve => setTimeout(resolve, 600)); 
        }
    }
});
