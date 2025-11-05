// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State Management
let currentUser = null;
let authToken = null;

// DOM Elements
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const loginBtn = document.getElementById('loginBtn');
const heroLoginBtn = document.getElementById('heroLoginBtn');
const closeModal = document.getElementById('closeModal');
const userSection = document.getElementById('userSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const toast = document.getElementById('toast');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAuth();
    initForms();
    initSearch();
    initBlockchain();
    checkStoredAuth();
});

// Navigation
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('data-section');
            showSection(sectionId);
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Load data for specific sections
        if (sectionId === 'blockchain' && authToken) {
            loadBlockchainInfo();
        }
    }
}

// Authentication
function initAuth() {
    loginBtn.addEventListener('click', () => openModal());
    heroLoginBtn.addEventListener('click', () => openModal());
    closeModal.addEventListener('click', () => closeModalFunc());
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleLogin();
    });
    
    // Close modal on outside click
    loginModal.addEventListener('click', (e) => {
        if (e.target === loginModal) {
            closeModalFunc();
        }
    });
}

function openModal() {
    loginModal.classList.add('active');
}

function closeModalFunc() {
    loginModal.classList.remove('active');
    document.getElementById('loginMessage').style.display = 'none';
}

async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            
            // Store in localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            updateUIAfterLogin();
            closeModalFunc();
            showToast(`Welcome, ${currentUser.name}!`, 'success');
            
            loginForm.reset();
        } else {
            showMessage('loginMessage', data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('loginMessage', 'Could not connect to server. Make sure the API is running.', 'error');
    } finally {
        showLoading(false);
    }
}

function checkStoredAuth() {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    
    if (storedToken && storedUser) {
        authToken = storedToken;
        currentUser = JSON.parse(storedUser);
        updateUIAfterLogin();
    }
}

function updateUIAfterLogin() {
    userSection.innerHTML = `
        <div class="user-info">
            <div class="user-avatar">
                ${currentUser.name.charAt(0).toUpperCase()}
            </div>
            <div class="user-details">
                <div class="user-name">${currentUser.name}</div>
                <div class="user-role">${currentUser.role}</div>
            </div>
            <button class="btn btn-outline" onclick="handleLogout()">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        </div>
    `;
    
    // Show/hide dashboard based on role
    if (currentUser.role === 'fiscalizer') {
        // Fiscalizer can access dashboard
    } else {
        // Hide create entry form for clients
        const dashboardLink = document.querySelector('[data-section="dashboard"]');
        if (dashboardLink) {
            dashboardLink.style.display = 'none';
        }
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    userSection.innerHTML = `
        <button class="btn btn-primary" id="loginBtn">
            <i class="fas fa-sign-in-alt"></i> Login
        </button>
    `;
    
    // Re-attach event listener
    document.getElementById('loginBtn').addEventListener('click', () => openModal());
    
    showToast('Logged out successfully', 'info');
    showSection('home');
}

// Forms
function initForms() {
    const createEntryForm = document.getElementById('createEntryForm');
    
    createEntryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleCreateEntry();
    });
    
    // Learn More button
    document.getElementById('learnMoreBtn').addEventListener('click', () => {
        showSection('query');
        document.querySelector('[data-section="query"]').classList.add('active');
        document.querySelector('[data-section="home"]').classList.remove('active');
    });
}

async function handleCreateEntry() {
    if (!authToken) {
        showToast('Please login first', 'error');
        openModal();
        return;
    }
    
    if (currentUser.role !== 'fiscalizer') {
        showToast('Only fiscalizers can create entries', 'error');
        return;
    }
    
    const formData = new FormData(document.getElementById('createEntryForm'));
    
    // Get certifications
    const certifications = [];
    document.querySelectorAll('input[name="cert"]:checked').forEach(checkbox => {
        certifications.push(checkbox.value);
    });
    
    const entryData = {
        coffee_batch: formData.get('coffeeBatch'),
        origin: formData.get('origin'),
        location: formData.get('location'),
        harvest_date: formData.get('harvestDate'),
        quality_grade: formData.get('qualityGrade'),
        weight_kg: parseInt(formData.get('weightKg')),
        processing_method: formData.get('processingMethod'),
        variety: formData.get('variety'),
        altitude_meters: formData.get('altitude') ? parseInt(formData.get('altitude')) : null,
        certifications: certifications,
        notes: formData.get('notes')
    };
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(entryData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('formMessage', 
                `✓ Entry added successfully! Block Hash: ${data.block.hash.substring(0, 16)}...`, 
                'success');
            document.getElementById('createEntryForm').reset();
            showToast('Coffee entry added to blockchain!', 'success');
        } else {
            showMessage('formMessage', data.error || 'Failed to create entry', 'error');
        }
    } catch (error) {
        console.error('Create entry error:', error);
        showMessage('formMessage', 'Could not connect to server', 'error');
    } finally {
        showLoading(false);
    }
}

// Search
function initSearch() {
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Search buttons
    document.getElementById('searchBatchBtn').addEventListener('click', () => searchByBatch());
    document.getElementById('searchOriginBtn').addEventListener('click', () => searchByOrigin());
    document.getElementById('loadAllBtn').addEventListener('click', () => loadAllEntries());
    
    // Enter key support
    document.getElementById('searchBatch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchByBatch();
    });
    document.getElementById('searchOrigin').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchByOrigin();
    });
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.search-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

async function searchByBatch() {
    if (!authToken) {
        showToast('Please login first', 'error');
        openModal();
        return;
    }
    
    const batchId = document.getElementById('searchBatch').value.trim();
    
    if (!batchId) {
        showToast('Please enter a batch ID', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/entries/batch/${batchId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data.entries);
        } else {
            showToast(data.error || 'Batch not found', 'error');
            hideResults();
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Could not connect to server', 'error');
    } finally {
        showLoading(false);
    }
}

async function searchByOrigin() {
    if (!authToken) {
        showToast('Please login first', 'error');
        openModal();
        return;
    }
    
    const origin = document.getElementById('searchOrigin').value.trim();
    
    if (!origin) {
        showToast('Please enter an origin/farm name', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/entries/origin/${encodeURIComponent(origin)}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data.entries);
        } else {
            showToast(data.error || 'No entries found', 'error');
            hideResults();
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Could not connect to server', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadAllEntries() {
    if (!authToken) {
        showToast('Please login first', 'error');
        openModal();
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/entries`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data.entries);
            showToast(`Loaded ${data.entries.length} entries`, 'success');
        } else {
            showToast('Failed to load entries', 'error');
        }
    } catch (error) {
        console.error('Load error:', error);
        showToast('Could not connect to server', 'error');
    } finally {
        showLoading(false);
    }
}

function displayResults(entries) {
    const resultsContainer = document.getElementById('searchResults');
    const resultsContent = document.getElementById('resultsContent');
    
    if (!entries || entries.length === 0) {
        hideResults();
        showToast('No entries found', 'info');
        return;
    }
    
    resultsContent.innerHTML = entries.map(entry => createEntryCard(entry)).join('');
    resultsContainer.style.display = 'block';
    
    // Smooth scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function createEntryCard(entry) {
    const data = entry.data;
    const certs = data.certifications || [];
    
    return `
        <div class="coffee-entry">
            <div class="entry-header">
                <div>
                    <h3 class="entry-title">
                        <i class="fas fa-coffee"></i> ${data.coffee_batch}
                    </h3>
                    <p style="color: var(--text-secondary);">
                        <i class="fas fa-map-marker-alt"></i> ${data.origin}
                    </p>
                </div>
                <span class="entry-badge badge-${data.quality_grade.toLowerCase()}">
                    <i class="fas fa-star"></i> Grade ${data.quality_grade}
                </span>
            </div>
            
            <div class="entry-grid">
                ${data.location ? `
                <div class="entry-item">
                    <i class="fas fa-globe"></i>
                    <div>
                        <div class="entry-label">Location</div>
                        <div class="entry-value">${data.location}</div>
                    </div>
                </div>
                ` : ''}
                
                <div class="entry-item">
                    <i class="fas fa-calendar"></i>
                    <div>
                        <div class="entry-label">Harvest Date</div>
                        <div class="entry-value">${data.harvest_date}</div>
                    </div>
                </div>
                
                <div class="entry-item">
                    <i class="fas fa-weight"></i>
                    <div>
                        <div class="entry-label">Weight</div>
                        <div class="entry-value">${data.weight_kg} kg</div>
                    </div>
                </div>
                
                ${data.processing_method ? `
                <div class="entry-item">
                    <i class="fas fa-cogs"></i>
                    <div>
                        <div class="entry-label">Processing</div>
                        <div class="entry-value">${data.processing_method}</div>
                    </div>
                </div>
                ` : ''}
                
                ${data.variety ? `
                <div class="entry-item">
                    <i class="fas fa-seedling"></i>
                    <div>
                        <div class="entry-label">Variety</div>
                        <div class="entry-value">${data.variety}</div>
                    </div>
                </div>
                ` : ''}
                
                ${data.altitude_meters ? `
                <div class="entry-item">
                    <i class="fas fa-mountain"></i>
                    <div>
                        <div class="entry-label">Altitude</div>
                        <div class="entry-value">${data.altitude_meters}m</div>
                    </div>
                </div>
                ` : ''}
                
                <div class="entry-item">
                    <i class="fas fa-user-check"></i>
                    <div>
                        <div class="entry-label">Verified By</div>
                        <div class="entry-value">${data.fiscalizer_id}</div>
                    </div>
                </div>
                
                <div class="entry-item">
                    <i class="fas fa-clock"></i>
                    <div>
                        <div class="entry-label">Block Time</div>
                        <div class="entry-value">${new Date(entry.timestamp).toLocaleString()}</div>
                    </div>
                </div>
            </div>
            
            ${certs.length > 0 ? `
            <div class="certifications">
                <strong><i class="fas fa-certificate"></i> Certifications:</strong>
                ${certs.map(cert => `<span class="cert-badge"><i class="fas fa-check"></i> ${cert}</span>`).join('')}
            </div>
            ` : ''}
            
            ${data.notes ? `
            <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: var(--border-radius);">
                <strong><i class="fas fa-sticky-note"></i> Notes:</strong>
                <p style="margin-top: 0.5rem;">${data.notes}</p>
            </div>
            ` : ''}
            
            <div class="blockchain-hash">
                <div class="hash-label">
                    <i class="fas fa-shield-alt"></i> Blockchain Verification
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Block Index: ${entry.index} | Nonce: ${entry.nonce}
                </div>
                <div style="font-size: 0.85rem; margin-top: 0.5rem; color: var(--success);">
                    Hash: ${entry.hash}
                </div>
            </div>
        </div>
    `;
}

function hideResults() {
    document.getElementById('searchResults').style.display = 'none';
}

// Blockchain
function initBlockchain() {
    document.getElementById('refreshBlockchainBtn').addEventListener('click', () => loadBlockchainInfo());
    document.getElementById('validateBlockchainBtn').addEventListener('click', () => validateBlockchain());
}

async function loadBlockchainInfo() {
    if (!authToken) {
        showToast('Please login first', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/blockchain/info`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('blockCount').textContent = data.length;
            document.getElementById('validStatus').textContent = data.is_valid ? '✓ Valid' : '✗ Invalid';
            document.getElementById('validStatus').style.color = data.is_valid ? 'var(--success)' : 'var(--danger)';
            document.getElementById('difficulty').textContent = data.difficulty;
            document.getElementById('entryCount').textContent = data.length - 1; // Exclude genesis block
            
            showToast('Blockchain info updated', 'success');
        } else {
            showToast('Failed to load blockchain info', 'error');
        }
    } catch (error) {
        console.error('Blockchain info error:', error);
        showToast('Could not connect to server', 'error');
    } finally {
        showLoading(false);
    }
}

async function validateBlockchain() {
    if (!authToken) {
        showToast('Please login first', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/blockchain/validate`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const validationResult = document.getElementById('validationResult');
            validationResult.textContent = data.message;
            validationResult.className = `message ${data.valid ? 'success' : 'error'}`;
            validationResult.style.display = 'block';
            
            showToast(data.message, data.valid ? 'success' : 'error');
        } else {
            showToast('Validation failed', 'error');
        }
    } catch (error) {
        console.error('Validation error:', error);
        showToast('Could not connect to server', 'error');
    } finally {
        showLoading(false);
    }
}

// Utility Functions
function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

function showMessage(elementId, message, type) {
    const messageEl = document.getElementById(elementId);
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = 'toast show';
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
