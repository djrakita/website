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
        fetch('publications.json')
            .then(response => response.json())
            .then(data => {
                pubContainer.innerHTML = ''; // Clear loading message

                data.forEach(category => {
                    // Skip objects that are not publication categories (like the comment/example object)
                    if (!category.category || !category.items) return;

                    const categoryHeader = document.createElement('h2');
                    categoryHeader.style.margin = '3rem 0 1rem';
                    categoryHeader.textContent = category.category;
                    pubContainer.appendChild(categoryHeader);

                    const listDiv = document.createElement('div');
                    listDiv.className = 'publication_list';

                    category.items.forEach(item => {
                        const pubDiv = document.createElement('div');
                        pubDiv.className = 'publication';

                        const pdfLink = item.pdf ? `
                            <a href="${item.pdf}" target="_blank" class="pdf_icon_link" title="Download PDF">
                                <svg class="pdf_icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                    <line x1="16" y1="13" x2="8" y2="13"></line>
                                    <line x1="16" y1="17" x2="8" y2="17"></line>
                                    <polyline points="10 9 9 9 8 9"></polyline>
                                </svg>
                            </a>
                        ` : '<div class="pdf_placeholder"></div>';

                        pubDiv.innerHTML = `
                            ${pdfLink}
                            <span>[${item.id}] ${item.authors} ${item.year}. ${item.title} <em>${item.venue}</em>.</span>
                        `;
                        listDiv.appendChild(pubDiv);
                    });

                    pubContainer.appendChild(listDiv);
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
        fetch('news.json')
            .then(response => response.json())
            .then(data => {
                newsContainer.innerHTML = '';
                const limit = 3;

                data.forEach((item, index) => {
                    const newsItem = document.createElement('div');
                    newsItem.className = 'news_item';
                    if (index >= limit) {
                        newsItem.classList.add('hidden');
                    }

                    newsItem.innerHTML = `
                        <span class="news_date">[${item.date}]</span> ${item.content}
                    `;
                    newsContainer.appendChild(newsItem);
                });

                if (data.length > limit) {
                    toggleNewsBtn.style.display = 'block';
                    let isExpanded = false;

                    toggleNewsBtn.addEventListener('click', () => {
                        isExpanded = !isExpanded;
                        const hiddenItems = newsContainer.querySelectorAll('.news_item');

                        hiddenItems.forEach((item, index) => {
                            if (index >= limit) {
                                if (isExpanded) {
                                    item.classList.remove('hidden');
                                } else {
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
