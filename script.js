document.addEventListener('DOMContentLoaded', () => {
    // Intersection Observer for Scroll Reveal
    const revealElements = document.querySelectorAll('[data-reveal]');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80, // Offset for sticky header
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add scrolled class to header on scroll
    const header = document.querySelector('.banner');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    // Video Carousel Logic
    const track = document.querySelector('.carousel_track');
    const slides = Array.from(document.querySelectorAll('.video_slide'));
    const nextBtn = document.querySelector('.carousel_btn.next');
    const prevBtn = document.querySelector('.carousel_btn.prev');

    if (track && slides.length > 0) {
        let currentIndex = 0;

        const updateCarousel = () => {
            const slideWidth = slides[0].getBoundingClientRect().width;
            track.style.transform = `translateX(-${currentIndex * slideWidth}px)`;

            // Update button states
            if (prevBtn) prevBtn.disabled = currentIndex === 0;
            if (nextBtn) nextBtn.disabled = currentIndex === slides.length - 1;
        };

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentIndex < slides.length - 1) {
                    currentIndex++;
                    updateCarousel();
                }
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateCarousel();
                }
            });
        }

        // Initialize button states
        updateCarousel();

        // Handle window resize
        window.addEventListener('resize', updateCarousel);
    }

    // Dynamic Publications Loading
    const pubContainer = document.getElementById('publications_container');
    if (pubContainer) {
        fetch('data/publications.yml')
            .then(response => response.text())
            .then(text => jsyaml.load(text))
            .then(data => {
                pubContainer.innerHTML = ''; // Clear loading message

                // Group by type (Apollo lab format uses 'type')
                const groupedData = {};
                data.forEach(item => {
                    if (!item.type || item.type === 'Preprint') return; // Skip Preprints
                    let catName = item.type === 'Journal' ? 'Journal Articles' : 
                                 (item.type === 'Conference' ? 'Conference Papers' : item.type + 's');
                    if (!groupedData[catName]) {
                        groupedData[catName] = [];
                    }
                    groupedData[catName].push(item);
                });

                const categories = Object.keys(groupedData).map(cat => ({
                    category: cat,
                    items: groupedData[cat]
                }));

                categories.forEach(category => {
                    // Skip objects that are not publication categories (like the comment/example object)
                    if (!category.category || !category.items) return;

                    const categoryHeader = document.createElement('h2');
                    categoryHeader.style.margin = '2.5rem 0 1rem';
                    categoryHeader.textContent = category.category;
                    pubContainer.appendChild(categoryHeader);

                    const listDiv = document.createElement('div');
                    listDiv.className = 'publication_list';

                    // Define limits for specific categories
                    let limit = Infinity;
                    if (category.category.includes('Journal Articles')) limit = 3;
                    if (category.category.includes('Conference Papers')) limit = 5;

                    category.items.forEach((item, index) => {
                        const pubDiv = document.createElement('div');
                        pubDiv.className = 'publication';
                        if (index >= limit) {
                            pubDiv.classList.add('hidden');
                        }

                        const pdfLink = item.link ? `
                            <a href="${item.link}" target="_blank" class="pdf_icon_link" title="Download PDF">
                                <svg class="pdf_icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                    <line x1="16" y1="13" x2="8" y2="13"></line>
                                    <line x1="16" y1="17" x2="8" y2="17"></line>
                                    <polyline points="10 9 9 9 8 9"></polyline>
                                </svg>
                            </a>
                        ` : '<div class="pdf_placeholder"></div>';

                        // Compute ID: e.g. [J<num>] or [C<num>]
                        let idPrefix = '';
                        if (category.category === 'Journal Articles') idPrefix = 'J';
                        else if (category.category === 'Conference Papers') idPrefix = 'C';
                        
                        let idStr = '';
                        if (idPrefix) {
                            const num = category.items.length - index;
                            idStr = `[${idPrefix}${num}] `;
                        }

                        let awardSuffix = '';
                        if (item.award) {
                            if (item.award.toLowerCase().includes('winner') || item.award.toLowerCase().includes('1st')) {
                                awardSuffix = ` <span class="award_icon trophy"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 5h-2V3H7v2H5C3.9 5 3 5.9 3 7v1c0 2.55 1.92 4.67 4.39 4.97C8.44 14.8 10.98 16.4 11 18.06V20H8v2h8v-2h-3v-1.94c.02-1.66 2.56-3.26 3.61-6.09C19.08 12.67 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm14 0c0 1.3-.84 2.4-2 2.82V7h2v1z"/></svg></span><strong style="color: #B43232;">${item.award}</strong>`;
                            } else {
                                awardSuffix = ` <span class="award_icon medal"><svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M12 15.2l-3.5 2.1.9-4-3.1-2.7 4.1-.3L12 6.6l1.6 3.7 4.1.3-3.1 2.7.9 4-3.5-2.1zM2 2h4l4.5 9-1.5 3L2 2zm16 0h4l-7 12-1.5-3L18 2z"/></svg></span><strong style="color: #B43232;">${item.award}</strong>`;
                            }
                        }

                        let presentationSuffix = '';
                        if (item.presentation === 'Oral') {
                            presentationSuffix = ` <span class="award_icon microphone"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg></span><strong style="color: #B43232;">Oral Presentation</strong>`;
                        }

                        pubDiv.innerHTML = `
                            ${pdfLink}
                            <span>${idStr}${item.authors} (${item.year}). <strong>${item.title}</strong> <em>${item.venue ? item.venue : ''}</em>.${awardSuffix}${presentationSuffix}</span>
                        `;
                        listDiv.appendChild(pubDiv);
                    });

                    pubContainer.appendChild(listDiv);

                    // Add toggle button if items exceed limit
                    if (category.items.length > limit) {
                        const toggleBtn = document.createElement('button');
                        toggleBtn.className = 'toggle_btn';
                        toggleBtn.textContent = `Show All ${category.category}`;
                        pubContainer.appendChild(toggleBtn);

                        let isExpanded = false;
                        toggleBtn.addEventListener('click', () => {
                            isExpanded = !isExpanded;
                            const items = listDiv.querySelectorAll('.publication');
                            items.forEach((item, index) => {
                                if (index >= limit) {
                                    if (isExpanded) {
                                        const delay = (index - limit) * 50; // slightly faster stagger for long lists
                                        item.style.transitionDelay = `${delay}ms`;
                                        item.classList.remove('hidden');
                                    } else {
                                        item.style.transitionDelay = '0ms';
                                        item.classList.add('hidden');
                                    }
                                }
                            });
                            toggleBtn.textContent = isExpanded ? 'Show Less' : `Show All ${category.category}`;
                            if (!isExpanded) {
                                categoryHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }
                        });
                    }
                });
            })
            .catch(error => {
                console.error('Error loading publications:', error);
                pubContainer.innerHTML = '<p>Error loading publications. Please try again later.</p>';
            });
    }
    // Dynamic News Loading
    const newsContainer = document.getElementById('news_container');
    const toggleNewsBtn = document.getElementById('toggle_news');

    if (newsContainer && toggleNewsBtn) {
        // Event delegation for news items expand/collapse
        newsContainer.addEventListener('click', (e) => {
            const summary = e.target.closest('.news_summary');
            if (!summary) return;
            
            const newsItem = summary.closest('.news_item');
            if (!newsItem) return;
            
            const isOpen = newsItem.classList.toggle('is_open');
            summary.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
        
        newsContainer.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                const summary = e.target.closest('.news_summary');
                if (summary) {
                    e.preventDefault();
                    summary.click();
                }
            }
        });

        fetch('data/news.yml')
            .then(response => response.text())
            .then(text => jsyaml.load(text))
            .then(data => {
                newsContainer.innerHTML = '';
                const limit = 3;

                data.forEach((item, index) => {
                    const hasContent = item.content && item.content.trim() !== '';
                    const newsItem = document.createElement('div');
                    newsItem.className = 'news_item';
                    if (index >= limit) {
                        newsItem.classList.add('hidden');
                    }

                    if (hasContent) {
                        newsItem.classList.add('news_expandable');
                        newsItem.innerHTML = `
                            <div class="news_summary" role="button" aria-expanded="false" tabindex="0">
                                <span class="news_summary_left">
                                    <span class="news_date">[${item.date}]</span> 
                                    <span class="news_title_text">${item.title || 'News Update'}</span>
                                </span>
                                <span class="expand_icon">▼</span>
                            </div>
                            <div class="news_content_wrapper">
                                <div class="news_content">
                                    ${item.content}
                                </div>
                            </div>
                        `;
                    } else {
                        newsItem.innerHTML = `
                            <div class="news_simple">
                                <span class="news_date">[${item.date}]</span> 
                                <span class="news_title_text">${item.title || 'News Update'}</span>
                            </div>
                        `;
                    }
                    newsContainer.appendChild(newsItem);
                });

                if (data.length > limit) {
                    toggleNewsBtn.style.display = 'block';
                    let isExpanded = false;

                    toggleNewsBtn.addEventListener('click', () => {
                        isExpanded = !isExpanded;
                        const allItems = newsContainer.querySelectorAll('.news_item');

                        allItems.forEach((item, index) => {
                            if (index >= limit) {
                                if (isExpanded) {
                                    // Stagger delay for each additional item
                                    const delay = (index - limit) * 100; // 100ms stagger
                                    item.style.transitionDelay = `${delay}ms`;
                                    item.classList.remove('hidden');
                                } else {
                                    // No delay when collapsing for a snappier feel
                                    item.style.transitionDelay = '0ms';
                                    item.classList.add('hidden');
                                }
                            }
                        });

                        toggleNewsBtn.textContent = isExpanded ? 'Show Less' : 'Show All News';

                        if (!isExpanded) {
                            // Smooth scroll back to news section top if collapsing
                            document.getElementById('news').scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error loading news:', error);
                newsContainer.innerHTML = '<p>Error loading news.</p>';
            });
    }

    // Return to Top Button Logic
    const returnToTop = document.querySelector('.return_to_top');
    if (returnToTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                returnToTop.classList.add('visible');
            } else {
                returnToTop.classList.remove('visible');
            }
        });
    }
});
