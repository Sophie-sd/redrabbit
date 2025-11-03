(function() {
  const slider = document.getElementById('reviewsSlider');
  if (!slider) return;
  
  const prevBtn = document.querySelector('.reviews-prev-btn');
  const nextBtn = document.querySelector('.reviews-next-btn');
  
  if (!prevBtn || !nextBtn) return;
  
  const getScrollAmount = () => {
    const cardWidth = slider.querySelector('.review-card')?.offsetWidth || 350;
    const gap = 24;
    return cardWidth + gap;
  };
  
  prevBtn.addEventListener('click', function() {
    slider.scrollBy({
      left: -getScrollAmount(),
      behavior: 'smooth'
    });
  });
  
  nextBtn.addEventListener('click', function() {
    slider.scrollBy({
      left: getScrollAmount(),
      behavior: 'smooth'
    });
  });
  
  function updateButtonsVisibility() {
    const isAtStart = slider.scrollLeft === 0;
    const isAtEnd = slider.scrollLeft + slider.clientWidth >= slider.scrollWidth - 1;
    
    prevBtn.disabled = isAtStart;
    nextBtn.disabled = isAtEnd;
  }
  
  slider.addEventListener('scroll', updateButtonsVisibility);
  window.addEventListener('resize', updateButtonsVisibility);
  updateButtonsVisibility();
  
  document.querySelectorAll('.review-read-more').forEach(btn => {
    btn.addEventListener('click', function() {
      const textEl = this.previousElementSibling;
      if (textEl) {
        textEl.style.webkitLineClamp = textEl.style.webkitLineClamp === 'unset' ? '4' : 'unset';
        this.textContent = textEl.style.webkitLineClamp === 'unset' ? 'Згорнути' : 'Більше...';
      }
    });
  });
})();
