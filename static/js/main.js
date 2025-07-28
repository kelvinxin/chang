// 启梦教育平台 - 主要JavaScript功能
// 现代化交互和用户体验

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initLanguageSwitcher();
    initSmoothScrolling();
    initAnimations();
    initFormValidation();
    initTooltips();
    initCarousel();
    initSpeechPractice();
    initNotifications();
    initTheme();
});

// 语言切换功能
function initLanguageSwitcher() {
    const languageButtons = document.querySelectorAll('.language-switcher .btn');
    const currentLang = localStorage.getItem('language') || 'zh';
    
    // 设置当前语言按钮为激活状态
    languageButtons.forEach(btn => {
        if (btn.dataset.lang === currentLang) {
            btn.classList.add('active');
        }
        
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.dataset.lang;
            
            // 移除所有激活状态
            languageButtons.forEach(b => b.classList.remove('active'));
            // 添加当前按钮激活状态
            this.classList.add('active');
            
            // 保存语言选择
            localStorage.setItem('language', lang);
            
            // 切换语言
            window.location.href = `/set_language/${lang}`;
        });
    });
}

// 平滑滚动
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 动画效果
function initAnimations() {
    // 滚动时触发动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // 观察所有卡片元素
    const cards = document.querySelectorAll('.card, .feature-card, .course-card');
    cards.forEach(card => {
        observer.observe(card);
    });
    
    // 数字计数动画
    const counters = document.querySelectorAll('.stat-number, .counter');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        let current = 0;
        const increment = target / 50;
        
        const updateCounter = () => {
            if (current < target) {
                current += increment;
                counter.textContent = Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // 当元素进入视口时开始计数
        const counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    counterObserver.unobserve(entry.target);
                }
            });
        });
        
        counterObserver.observe(counter);
    });
}

// 表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
        
        // 实时验证
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // 必填验证
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = '此字段为必填项';
    }
    
    // 邮箱验证
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = '请输入有效的邮箱地址';
        }
    }
    
    // 电话验证
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = '请输入有效的电话号码';
        }
    }
    
    // 密码验证
    if (field.type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = '密码至少需要6个字符';
        }
    }
    
    // 更新UI
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        removeErrorMessage(field);
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showErrorMessage(field, errorMessage);
    }
    
    return isValid;
}

function showErrorMessage(field, message) {
    removeErrorMessage(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function removeErrorMessage(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// 工具提示
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 轮播图增强
function initCarousel() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
        // 自动播放控制
        const playButton = carousel.querySelector('.carousel-play-pause');
        if (playButton) {
            let isPlaying = true;
            
            playButton.addEventListener('click', function() {
                const carouselInstance = bootstrap.Carousel.getInstance(carousel);
                
                if (isPlaying) {
                    carouselInstance.pause();
                    this.innerHTML = '<i class="fas fa-play"></i>';
                    isPlaying = false;
                } else {
                    carouselInstance.cycle();
                    this.innerHTML = '<i class="fas fa-pause"></i>';
                    isPlaying = true;
                }
            });
        }
        
        // 触摸滑动支持
        let startX = 0;
        let endX = 0;
        
        carousel.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
        });
        
        carousel.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].clientX;
            handleSwipe();
        });
        
        function handleSwipe() {
            const threshold = 50;
            const diff = startX - endX;
            
            if (Math.abs(diff) > threshold) {
                const carouselInstance = bootstrap.Carousel.getInstance(carousel);
                if (diff > 0) {
                    carouselInstance.next();
                } else {
                    carouselInstance.prev();
                }
            }
        }
    });
}

// AI口语练习功能
function initSpeechPractice() {
    const recordButton = document.getElementById('recordButton');
    const playButton = document.getElementById('playButton');
    const textInput = document.getElementById('practiceText');
    const topicSelect = document.getElementById('topicSelect');
    const scoreDisplay = document.getElementById('scoreDisplay');
    
    if (!recordButton) return;
    
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('您的浏览器不支持录音功能', 'warning');
        recordButton.disabled = true;
        return;
    }
    
    // 录音按钮事件
    recordButton.addEventListener('click', function() {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });
    
    // 播放按钮事件
    if (playButton) {
        playButton.addEventListener('click', function() {
            playLastRecording();
        });
    }
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = function() {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                processRecording(audioBlob);
            };
            
            mediaRecorder.start();
            isRecording = true;
            
            // 更新UI
            recordButton.classList.add('recording');
            recordButton.innerHTML = '<i class="fas fa-stop"></i> 停止录音';
            recordButton.style.background = 'linear-gradient(135deg, #f44336, #d32f2f)';
            
            showNotification('开始录音...', 'info');
            
        } catch (error) {
            console.error('录音失败:', error);
            showNotification('录音失败，请检查麦克风权限', 'error');
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            
            // 恢复UI
            recordButton.classList.remove('recording');
            recordButton.innerHTML = '<i class="fas fa-microphone"></i> 开始录音';
            recordButton.style.background = '';
            
            showNotification('录音完成，正在分析...', 'info');
        }
    }
    
    async function processRecording(audioBlob) {
        const text = textInput.value.trim();
        const topic = topicSelect.value;
        
        if (!text) {
            showNotification('请先输入要练习的文本', 'warning');
            return;
        }
        
        try {
            // 转换音频为base64
            const audioBase64 = await blobToBase64(audioBlob);
            
            // 发送到后端进行AI分析
            const response = await fetch('/api/speech_evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio: audioBase64,
                    text: text,
                    topic: topic
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                displayScore(result);
                showNotification('语音分析完成！', 'success');
            } else {
                showNotification('语音分析失败，请重试', 'error');
            }
            
        } catch (error) {
            console.error('处理录音失败:', error);
            showNotification('处理录音失败，请重试', 'error');
        }
    }
    
    function displayScore(result) {
        if (!scoreDisplay) return;
        
        const scoreHtml = `
            <div class="score-display">
                <div class="score-number">${result.score}</div>
                <div class="score-label">总分</div>
                <div class="score-breakdown">
                    <div class="score-item">
                        <div class="score-value">${result.pronunciation_score}</div>
                        <div class="score-label">发音</div>
                    </div>
                    <div class="score-item">
                        <div class="score-value">${result.fluency_score}</div>
                        <div class="score-label">流利度</div>
                    </div>
                </div>
                <div class="feedback-text mt-3">
                    <h6>详细反馈：</h6>
                    <p>${result.feedback}</p>
                </div>
            </div>
        `;
        
        scoreDisplay.innerHTML = scoreHtml;
        scoreDisplay.style.display = 'block';
        
        // 添加动画效果
        scoreDisplay.classList.add('fade-in-up');
    }
    
    function blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
}

// 通知系统
function initNotifications() {
    // 创建通知容器
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = `
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: none;
        border-radius: 8px;
    `;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <i class="${icons[type] || icons.info}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 150);
        }
    }, duration);
}

// 主题切换
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // 更新按钮图标
        const icon = this.querySelector('i');
        if (newTheme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    });
}

// 搜索功能
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // 点击外部关闭搜索结果
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            hideSearchResults();
        }
    });
    
    async function performSearch(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            displaySearchResults(results);
        } catch (error) {
            console.error('搜索失败:', error);
        }
    }
    
    function displaySearchResults(results) {
        if (!searchResults) return;
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-no-results">未找到相关结果</div>';
        } else {
            const resultsHtml = results.map(result => `
                <div class="search-result-item">
                    <h6><a href="${result.url}">${result.title}</a></h6>
                    <p>${result.description}</p>
                </div>
            `).join('');
            
            searchResults.innerHTML = resultsHtml;
        }
        
        searchResults.style.display = 'block';
    }
    
    function hideSearchResults() {
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    }
}

// 文件上传增强
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.className = 'file-upload-wrapper';
        
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        // 创建自定义上传区域
        const uploadArea = document.createElement('div');
        uploadArea.className = 'file-upload-area';
        uploadArea.innerHTML = `
            <div class="file-upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <div class="file-upload-text">
                <p>点击选择文件或拖拽文件到此处</p>
                <small>支持的文件格式：PDF, DOC, PPT, MP3, MP4</small>
            </div>
        `;
        
        wrapper.appendChild(uploadArea);
        
        // 拖拽上传
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                updateFileDisplay(input, files[0]);
            }
        });
        
        // 点击上传
        uploadArea.addEventListener('click', function() {
            input.click();
        });
        
        // 文件选择
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFileDisplay(this, this.files[0]);
            }
        });
        
        function updateFileDisplay(input, file) {
            const uploadArea = input.parentNode.querySelector('.file-upload-area');
            uploadArea.innerHTML = `
                <div class="file-selected">
                    <i class="fas fa-file"></i>
                    <span>${file.name}</span>
                    <small>(${formatFileSize(file.size)})</small>
                </div>
            `;
        }
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 数据表格增强
function initDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // 添加搜索功能
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = '搜索...';
        
        table.parentNode.insertBefore(searchInput, table);
        
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
        
        // 添加排序功能
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort"></i>';
            
            header.addEventListener('click', function() {
                const column = this.dataset.sort;
                const isAsc = this.classList.contains('sort-asc');
                
                // 移除其他列的排序状态
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                    h.querySelector('i').className = 'fas fa-sort';
                });
                
                // 设置当前列的排序状态
                if (isAsc) {
                    this.classList.add('sort-desc');
                    this.querySelector('i').className = 'fas fa-sort-down';
                } else {
                    this.classList.add('sort-asc');
                    this.querySelector('i').className = 'fas fa-sort-up';
                }
                
                sortTable(table, column, !isAsc);
            });
        });
    });
}

function sortTable(table, column, ascending) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-value="${column}"]`)?.textContent || '';
        const bValue = b.querySelector(`[data-value="${column}"]`)?.textContent || '';
        
        if (ascending) {
            return aValue.localeCompare(bValue, 'zh-CN', { numeric: true });
        } else {
            return bValue.localeCompare(aValue, 'zh-CN', { numeric: true });
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// 工具函数
const utils = {
    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 节流函数
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // 格式化日期
    formatDate: function(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day);
    },
    
    // 复制到剪贴板
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('已复制到剪贴板', 'success');
            });
        } else {
            // 兼容旧浏览器
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showNotification('已复制到剪贴板', 'success');
        }
    }
};

// 导出工具函数到全局
window.utils = utils;
window.showNotification = showNotification;